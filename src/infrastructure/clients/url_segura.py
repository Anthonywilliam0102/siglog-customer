"""Validação das URLs de integração informadas pela equipe (o servidor vai chamá-las: evita SSRF básico)."""
import ipaddress
import socket
from urllib.parse import urlparse

from src.domain.errors import DomainError


def _publico(ip: str) -> bool:
    a = ipaddress.ip_address(ip)
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved or a.is_multicast or a.is_unspecified)


def resolver(host: str, porta: int) -> list[str]:
    return sorted({info[4][0] for info in socket.getaddrinfo(host, porta, type=socket.SOCK_STREAM)})


def validar_base_url(url: str, resolve=resolver) -> str:
    """Aceita só https para endereço público. Devolve a URL normalizada (sem barra final)."""
    u = (url or "").strip().rstrip("/")
    p = urlparse(u)
    if p.scheme != "https" or not p.hostname:
        raise DomainError("Use uma URL completa começando com https://")
    if p.username or p.password or p.query or p.fragment:
        raise DomainError("A URL não pode ter usuário, senha, parâmetros ou fragmento")
    if p.port not in (None, 443, 8443):
        raise DomainError("Porta não permitida (use 443 ou 8443)")
    try:
        ips = [p.hostname] if _eh_ip(p.hostname) else resolve(p.hostname, p.port or 443)
    except OSError as exc:
        raise DomainError("Não foi possível resolver o endereço informado") from exc
    if not ips or not all(_publico(i) for i in ips):
        raise DomainError("Endereço não permitido (rede interna ou local)")
    return u


def _eh_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
