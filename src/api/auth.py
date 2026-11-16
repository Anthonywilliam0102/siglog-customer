"""Autenticação JWT (HS256). Compatível com tokens do Supabase Auth usando o JWT secret do projeto.

Claims esperadas: `sub` (id do usuário) e `role` (cliente | atendente | gestor).
NOTA: no Supabase o papel customizado costuma ir em `app_metadata.role`; aceitamos as duas formas.
"""
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services import Actor
from src.config.settings import settings
from src.domain.rules import Role

bearer = HTTPBearer(auto_error=False)


def get_actor(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Actor:
    if creds is None:
        raise HTTPException(401, "Token ausente")
    if not settings.jwt_secret:
        raise HTTPException(500, "Autenticação não configurada (JWT_SECRET)")
    try:
        claims = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=["HS256"],
                            options={"verify_aud": False})
        role = claims.get("role") or (claims.get("app_metadata") or {}).get("role")
        return Actor(sub=str(claims["sub"]), role=Role(role))
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(401, "Token inválido") from exc
