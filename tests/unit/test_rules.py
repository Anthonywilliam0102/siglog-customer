from datetime import timedelta
from decimal import Decimal

import pytest

from src.domain import rules
from src.domain.errors import DomainError
from src.domain.rules import Prioridade


def test_cpf_valido_e_invalido():
    assert rules.normalizar_documento("529.982.247-25", "PF") == "52998224725"
    with pytest.raises(DomainError):
        rules.normalizar_documento("111.111.111-11", "PF")
    with pytest.raises(DomainError):
        rules.normalizar_documento("52998224726", "PF")


def test_cnpj_valido_e_invalido():
    assert rules.normalizar_documento("11.222.333/0001-81", "PJ") == "11222333000181"
    with pytest.raises(DomainError):
        rules.normalizar_documento("11222333000182", "PJ")


def test_sla_por_prioridade():
    now = rules.utcnow()
    assert rules.sla_due(Prioridade.ALTA, now) - now == timedelta(hours=4)
    assert rules.sla_due(Prioridade.MEDIA, now) - now == timedelta(hours=24)
    assert rules.sla_due(Prioridade.BAIXA, now) - now == timedelta(hours=72)


def test_cotacao_expira():
    now = rules.utcnow()
    assert rules.cotacao_expirada(now - timedelta(seconds=1), now)
    assert not rules.cotacao_expirada(now + timedelta(hours=1), now)


def test_estimativa_valor():
    assert rules.estimar_valor(100, 1) == Decimal("250.00")


@pytest.mark.parametrize("nota", [0, 6, -1])
def test_nota_invalida(nota):
    with pytest.raises(DomainError):
        rules.validar_nota(nota)


def test_envelope_de_evento_tem_campos_obrigatorios():
    from src.domain.events import envelope

    e = envelope("PedidoCriado", {"pedido_id": "x"})
    assert {"event_id", "event_type", "version", "occurred_at", "producer", "correlation_id", "data"} <= e.keys()
