from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import settings

_connect_args = {}
if settings.database_url.startswith("postgresql"):
    # Pooler do Supabase (modo transaction) não suporta prepared statements do psycopg 3.
    _connect_args["prepare_threshold"] = None

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    session: Session = SessionLocal()
    # O commit NÃO fica aqui: o teardown de dependências com yield roda depois que a resposta
    # já foi enviada. As rotas de escrita chamam `commit()` (api/routes.py) antes de retornar.
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
