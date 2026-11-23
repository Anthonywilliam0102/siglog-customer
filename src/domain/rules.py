"""Regras de negócio puras (sem framework). Ver docs/02_requirements.md (RN01–RN06)."""
import re
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from src.domain.errors import DomainError


class Role(StrEnum):
    CLIENTE = "cliente"
    ATENDENTE = "atendente"
    GESTOR = "gestor"


STAFF = {Role.ATENDENTE, Role.GESTOR}


class PedidoStatus(StrEnum):
    CRIADO = "CRIADO"
    EM_SEPARACAO = "EM_SEPARACAO"
    EM_TRANSPORTE = "EM_TRANSPORTE"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# RN07: transições permitidas do pedido (ENTREGUE e CANCELADO são finais).
TRANSICOES_PEDIDO = {
    PedidoStatus.CRIADO: {PedidoStatus.EM_SEPARACAO, PedidoStatus.CANCELADO},
    PedidoStatus.EM_SEPARACAO: {PedidoStatus.EM_TRANSPORTE, PedidoStatus.CANCELADO},
    PedidoStatus.EM_TRANSPORTE: {PedidoStatus.ENTREGUE},
    PedidoStatus.ENTREGUE: set(),
    PedidoStatus.CANCELADO: set(),
}


def transicao_valida(atual: str, novo: str) -> bool:
    return PedidoStatus(novo) in TRANSICOES_PEDIDO[PedidoStatus(atual)]


class Prioridade(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


class TicketStatus(StrEnum):
    ABERTO = "ABERTO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    RESOLVIDO = "RESOLVIDO"


class FeedbackTarget(StrEnum):
    ENTREGA = "ENTREGA"
    ATENDIMENTO = "ATENDIMENTO"


SLA_HORAS = {Prioridade.ALTA: 4, Prioridade.MEDIA: 24, Prioridade.BAIXA: 72}
COTACAO_VALIDADE = timedelta(hours=24)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def sla_due(prioridade: Prioridade, start: datetime | None = None) -> datetime:
    return (start or utcnow()) + timedelta(hours=SLA_HORAS[prioridade])


def cotacao_expirada(expires_at: datetime, now: datetime | None = None) -> bool:
    return as_aware(expires_at) <= (now or utcnow())


def estimar_valor(peso_kg: float, volume_m3: float) -> Decimal:
    """Estimativa simples (placeholder). O cálculo oficial do frete é do Financeiro."""
    valor = Decimal("50") + Decimal(str(peso_kg)) * Decimal("0.80") + Decimal(str(volume_m3)) * Decimal("120")
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validar_nota(nota: int) -> int:
    if not 1 <= nota <= 5:
        raise DomainError("A nota deve estar entre 1 e 5")
    return nota


def _cpf_ok(d: str) -> bool:
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        s = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        if int(d[n]) != (s * 10 % 11) % 10:
            return False
    return True


def _cnpj_ok(d: str) -> bool:
    if len(d) != 14 or d == d[0] * 14:
        return False
    for n, pesos in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        s = sum(int(d[i]) * pesos[i] for i in range(n))
        dv = 0 if s % 11 < 2 else 11 - s % 11
        if int(d[n]) != dv:
            return False
    return True


def normalizar_documento(documento: str, tipo: str) -> str:
    d = re.sub(r"\D", "", documento)
    ok = _cpf_ok(d) if tipo == "PF" else _cnpj_ok(d)
    if not ok:
        raise DomainError(f"Documento inválido para {tipo}")
    return d
