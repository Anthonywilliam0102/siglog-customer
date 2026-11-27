"""Tela de Configurações: URL e chave de API de integração com outros squads (chave cifrada, nunca devolvida)."""
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from src.config.settings import settings
from src.infrastructure import models as m
from src.infrastructure.clients import tracking, url_segura
from src.infrastructure.segredos import decifrar
from tests.integration.test_fluxo_api import _criar_cliente, _pedido

CHAVE = "chave-secreta-do-outro-squad-123"


@pytest.fixture()
def cripto(monkeypatch):
    monkeypatch.setattr(settings, "settings_encryption_key", Fernet.generate_key().decode())


@pytest.fixture()
def dns_publico(monkeypatch):
    monkeypatch.setattr(url_segura, "resolver", lambda host, porta: ["93.184.216.34"])  # IP público qualquer
    monkeypatch.setattr("src.application.services.validar_base_url",
                        lambda u: url_segura.validar_base_url(u, resolve=lambda h, p: ["93.184.216.34"]))


def test_so_a_equipe_ve_e_altera(client, cliente, atendente):
    assert client.get("/settings/integrations", headers=cliente).status_code == 403
    assert client.put("/settings/integrations/tracking", json={"header_name": "X-Key"}, headers=cliente).status_code == 403
    lista = client.get("/settings/integrations", headers=atendente).json()
    assert [i["squad"] for i in lista] == ["wms", "frota", "tracking", "financeiro", "rh"]
    assert all(not i["tem_chave"] and i["base_url"] is None for i in lista)


def test_chave_e_guardada_cifrada_e_nunca_devolvida(client, atendente, cripto, dns_publico, session_factory):
    r = client.put("/settings/integrations/tracking", headers=atendente,
                   json={"base_url": "https://tracking.exemplo.com/", "header_name": "X-Api-Key", "api_key": CHAVE})
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["tem_chave"] is True and corpo["base_url"] == "https://tracking.exemplo.com"
    assert CHAVE not in r.text and CHAVE not in client.get("/settings/integrations", headers=atendente).text
    with session_factory() as s:
        cfg = s.scalar(select(m.IntegrationSetting).where(m.IntegrationSetting.squad == "tracking"))
        assert cfg.api_key_enc != CHAVE and decifrar(cfg.api_key_enc) == CHAVE
        assert cfg.updated_by == "user-atendente"
    r = client.put("/settings/integrations/tracking", json={"limpar_chave": True}, headers=atendente)
    assert r.json()["tem_chave"] is False


def test_sem_chave_de_criptografia_no_servidor_recusa_a_chave(client, atendente, monkeypatch, dns_publico):
    monkeypatch.setattr(settings, "settings_encryption_key", "")
    r = client.put("/settings/integrations/wms", json={"api_key": CHAVE}, headers=atendente)
    assert r.status_code == 409 and "SETTINGS_ENCRYPTION_KEY" in r.json()["detail"]
    # a URL, sem chave, pode ser salva mesmo assim
    r = client.put("/settings/integrations/wms", json={"base_url": "https://wms.exemplo.com"}, headers=atendente)
    assert r.status_code == 200


@pytest.mark.parametrize("url", ["http://tracking.exemplo.com", "https://127.0.0.1", "https://10.0.0.5", "https://169.254.169.254/latest",
                                 "https://usuario:senha@exemplo.com", "ftp://x.com", "tracking.exemplo.com"])
def test_urls_inseguras_sao_recusadas(client, atendente, url):
    r = client.put("/settings/integrations/tracking", json={"base_url": url}, headers=atendente)
    assert r.status_code == 422, (url, r.text)


def test_nome_publico_que_resolve_para_ip_interno_e_recusado():
    from src.domain.errors import DomainError
    with pytest.raises(DomainError):
        url_segura.validar_base_url("https://pegadinha.exemplo.com", resolve=lambda h, p: ["10.1.2.3"])


def test_squad_inexistente_e_validacao_do_cabecalho(client, atendente):
    assert client.put("/settings/integrations/inexistente", json={}, headers=atendente).status_code == 404
    assert client.put("/settings/integrations/wms", json={"header_name": "ruim cabecalho!"}, headers=atendente).status_code == 422


def test_rastreamento_usa_a_integracao_configurada_com_a_chave(client, cliente, atendente, cripto, dns_publico, monkeypatch):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    monkeypatch.setattr(settings, "tracking_mock", True)  # a configuração da tela tem prioridade sobre o simulado
    client.put("/settings/integrations/tracking", headers=atendente,
               json={"base_url": "https://tracking.exemplo.com", "header_name": "X-Api-Key", "api_key": CHAVE})
    visto = {}

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "IN_TRANSIT", "events": []}

    def falso(url, timeout, headers=None, **kw):
        visto.update(url=url, headers=headers)
        return Resp()

    monkeypatch.setattr(tracking.httpx, "get", falso)
    r = client.get(f"/orders/{oid}/tracking", headers=cliente).json()
    assert r["source"] == "tracking" and r["status"] == "Em trânsito"
    assert visto["url"] == f"https://tracking.exemplo.com/tracking/orders/{oid}"
    assert visto["headers"] == {"X-Api-Key": CHAVE}
