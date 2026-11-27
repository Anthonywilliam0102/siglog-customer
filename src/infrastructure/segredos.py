"""Criptografia das chaves de API de integração guardadas no banco (Fernet).

A chave é gravada cifrada e NUNCA é devolvida pela API; só o backend a decifra para chamar o serviço do outro squad.
Gere a chave de criptografia com:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
e defina em SETTINGS_ENCRYPTION_KEY (variável de ambiente do servidor; nunca no repositório).
"""
from cryptography.fernet import Fernet, InvalidToken

from src.config.settings import settings
from src.domain.errors import Conflict


def _fernet() -> Fernet:
    if not settings.settings_encryption_key:
        raise Conflict("Para guardar chaves de API, defina SETTINGS_ENCRYPTION_KEY no servidor.")
    try:
        return Fernet(settings.settings_encryption_key.encode())
    except (ValueError, TypeError) as exc:
        raise Conflict("SETTINGS_ENCRYPTION_KEY inválida (use uma chave Fernet).") from exc


def cifrar(texto: str) -> str:
    return _fernet().encrypt(texto.encode()).decode()


def decifrar(token: str) -> str | None:
    """Devolve o texto, ou None se a chave de criptografia mudou (o valor guardado ficou ilegível)."""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, Conflict):
        return None
