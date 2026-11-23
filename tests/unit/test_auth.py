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
