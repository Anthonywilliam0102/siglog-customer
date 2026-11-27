from src.infrastructure.domain_metrics import DomainCollector
from tests.integration.test_fluxo_api import CLIENTE, _criar_cliente


def test_collector_expoe_metricas_de_dominio(client, cliente, session_factory):
    cid = _criar_cliente(client, cliente)
    client.post("/tickets", json={"customer_id": cid, "categoria": "DUVIDA", "assunto": "Dúvida", "mensagem": "Oi"},
                headers=cliente)
    metricas = {f.name: f for f in DomainCollector(session_factory).collect()}
    assert metricas["siglog_customers"].samples[0].value == 1
    assert metricas["siglog_tickets"].samples[0].labels["status"] == "ABERTO"
    assert metricas["siglog_tickets_sla_breached"].samples[0].value == 0
    assert CLIENTE  # dado fictício reutilizado do fluxo principal


def test_collector_nao_quebra_sem_banco():
    def quebrado():
        raise RuntimeError("db fora")

    assert list(DomainCollector(quebrado).collect()) == []
