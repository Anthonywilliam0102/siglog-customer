import time

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.config.settings import settings
from src.infrastructure.db import get_session
from src.infrastructure.models import Base

SECRET = "segredo-de-teste-com-mais-de-32-caracteres"


def make_token(sub: str, role: str, **extra) -> dict:
    claims = {"sub": sub, "role": role, "exp": int(time.time()) + 3600, **extra}
    token = jwt.encode(claims, SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def client(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", SECRET)

    def _get_session():
        s = session_factory()
        try:
            yield s
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    app.dependency_overrides[get_session] = _get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def cliente():
    return make_token("user-cliente-1", "cliente")


@pytest.fixture()
def outro_cliente():
    return make_token("user-cliente-2", "cliente")


@pytest.fixture()
def atendente():
    return make_token("user-atendente", "atendente")
