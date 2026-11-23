from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
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
