"""Autenticação JWT.

Aceita dois tipos de token:
- HS256 com `JWT_SECRET` (desenvolvimento e Supabase com chave legada);
- ES256/RS256 validados pelo JWKS do Supabase (`SUPABASE_URL`), o padrão dos projetos novos.

Perfil (`cliente` | `atendente` | `gestor`): vem de `app_metadata.role` (só o servidor altera) ou da
claim `role`. O `role: "authenticated"` do Supabase vira `cliente` (menor privilégio). `anon`,
`service_role` e qualquer outro valor são rejeitados. NUNCA ler perfil de `user_metadata` (o usuário edita).
"""
import logging
from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.application import services as svc
from src.application.services import Actor
from src.config.settings import settings
from src.domain.rules import Role
from src.infrastructure.db import get_session

bearer = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)


@lru_cache
def _jwks() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json", cache_keys=True)


def _decode(token: str) -> dict:
    alg = jwt.get_unverified_header(token).get("alg")
    if alg == "HS256":
        if not settings.jwt_secret:  # em produção, sem JWT_SECRET só valem tokens do Supabase (ES256)
            raise jwt.InvalidAlgorithmError("HS256 desabilitado")
        key, algs = settings.jwt_secret, ["HS256"]
    elif alg in ("ES256", "RS256") and settings.supabase_url:
        key, algs = _jwks().get_signing_key_from_jwt(token).key, [alg]
    else:
        raise jwt.InvalidAlgorithmError("algoritmo não aceito")
    return jwt.decode(token, key, algorithms=algs, leeway=settings.jwt_leeway_seconds,
                      options={"verify_aud": False, "require": ["exp", "sub"]})


def _role(claims: dict) -> Role:
    raw = (claims.get("app_metadata") or {}).get("role") or claims.get("role")
    if raw == "authenticated":
        raw = Role.CLIENTE
    return Role(raw)  # ValueError para anon, service_role, ausente ou desconhecido


def get_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Actor:
    if creds is None:
        raise HTTPException(401, "Token ausente")
    try:
        claims = _decode(creds.credentials)
        return Actor(sub=str(claims["sub"]), role=_role(claims))
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        # Registra só o tipo do erro (nunca o token) para diagnosticar 401 intermitente.
        log.warning('{"event": "auth_failed", "level": "WARNING", "reason": "%s"}', type(exc).__name__)
        raise HTTPException(401, "Token inválido") from exc


def get_actor_ou_chave(creds: HTTPAuthorizationCredentials | None = Depends(bearer),
                       x_api_key: str | None = Header(None), session: Session = Depends(get_session)) -> Actor:
    """Só para rotas de LEITURA que os outros squads podem chamar: aceita `X-API-Key` (emitida por nós) ou o JWT."""
    if x_api_key:
        ator = svc.ator_da_chave(session, x_api_key)
        if ator is None:
            raise HTTPException(401, "Chave de API inválida ou revogada")
        return ator
    return get_actor(creds)
