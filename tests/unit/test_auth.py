import time

import jwt
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config.settings import settings
from tests.conftest import SECRET


@pytest.fixture()
def c(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    return TestClient(app)


def _h(**claims):
    return {"Authorization": "Bearer " + jwt.encode(claims, SECRET, algorithm="HS256")}


def test_token_sem_exp_e_rejeitado(c):
    assert c.get("/customers/00000000-0000-0000-0000-000000000000", headers=_h(sub="u", role="cliente")).status_code == 401


def test_token_expirado_e_rejeitado(c):
    h = _h(sub="u", role="cliente", exp=int(time.time()) - 10)
    assert c.get("/customers/00000000-0000-0000-0000-000000000000", headers=h).status_code == 401


def test_token_com_perfil_desconhecido_e_rejeitado(c):
    h = _h(sub="u", role="root", exp=int(time.time()) + 60)
    assert c.get("/customers/00000000-0000-0000-0000-000000000000", headers=h).status_code == 401


# ---- tokens no formato do Supabase ----
from types import SimpleNamespace  # noqa: E402

from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials  # noqa: E402

from src.api import auth  # noqa: E402


def _actor(token):
    return auth.get_actor(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))


def _hs(**claims):
    claims.setdefault("exp", int(time.time()) + 60)
    return jwt.encode(claims, SECRET, algorithm="HS256")


def test_supabase_authenticated_vira_cliente(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    assert _actor(_hs(sub="u1", role="authenticated")).role == "cliente"


def test_app_metadata_define_o_perfil(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    a = _actor(_hs(sub="u1", role="authenticated", app_metadata={"role": "atendente"}))
    assert a.role == "atendente" and a.is_staff


def test_user_metadata_nao_define_perfil(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    a = _actor(_hs(sub="u1", role="authenticated", user_metadata={"role": "gestor"}))
    assert a.role == "cliente" and not a.is_staff


@pytest.mark.parametrize("role", ["anon", "service_role", "postgres"])
def test_roles_do_supabase_que_nao_sao_de_negocio_sao_rejeitados(monkeypatch, role):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    with pytest.raises(HTTPException) as e:
        _actor(_hs(sub="u1", role=role))
    assert e.value.status_code == 401


def test_token_es256_validado_pelo_jwks(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    token = jwt.encode({"sub": "u9", "role": "authenticated", "exp": int(time.time()) + 60}, key,
                       algorithm="ES256", headers={"kid": "k1"})
    monkeypatch.setattr(settings, "supabase_url", "https://exemplo.supabase.co")
    fake = SimpleNamespace(get_signing_key_from_jwt=lambda t: SimpleNamespace(key=key.public_key()))
    monkeypatch.setattr(auth, "_jwks", lambda: fake)
    assert _actor(token).sub == "u9"


def test_es256_sem_supabase_url_e_rejeitado(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    token = jwt.encode({"sub": "u9", "role": "authenticated", "exp": int(time.time()) + 60}, key, algorithm="ES256")
    monkeypatch.setattr(settings, "supabase_url", "")
    with pytest.raises(HTTPException) as e:
        _actor(token)
    assert e.value.status_code == 401


def test_algoritmo_none_e_rejeitado(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)
    token = jwt.encode({"sub": "u", "role": "gestor", "exp": int(time.time()) + 60}, None, algorithm="none")
    with pytest.raises(HTTPException) as e:
        _actor(token)
    assert e.value.status_code == 401
