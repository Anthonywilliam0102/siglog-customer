"""Rodada de testes de segurança (caixa-preta contra a API em memória): autenticação, autorização (RN02/IDOR),
entrada de dados, SSRF, chaves de API e exposição de informação."""
import base64
import json
import time

import jwt
import pytest

from src.config.settings import settings
from src.infrastructure.clients import url_segura
from tests.conftest import SECRET, make_token
from tests.integration.test_fluxo_api import _criar_cliente, _pedido

ROTAS_PROTEGIDAS = [("GET", "/orders"), ("GET", "/customers"), ("GET", "/tickets"), ("GET", "/claims"), ("GET", "/me"),
                    ("GET", "/settings/integrations"), ("GET", "/settings/api-keys"), ("GET", "/integrations/status")]


# ---------- autenticação ----------
@pytest.mark.parametrize("metodo,rota", ROTAS_PROTEGIDAS)
def test_sem_token_e_negado(client, metodo, rota):
    assert client.request(metodo, rota).status_code == 401


def _b64(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()


def test_tokens_forjados_ou_invalidos_sao_negados(client):
    agora = int(time.time())
    candidatos = {
        "alg none": f"{_b64({'alg': 'none', 'typ': 'JWT'})}.{_b64({'sub': 'x', 'role': 'gestor', 'exp': agora + 600})}.",
        "assinatura errada": jwt.encode({"sub": "x", "role": "gestor", "exp": agora + 600}, "outro-segredo-qualquer-1234567890abcdef", algorithm="HS256"),
        "expirado": jwt.encode({"sub": "x", "role": "cliente", "exp": agora - 600}, SECRET, algorithm="HS256"),
        "sem exp": jwt.encode({"sub": "x", "role": "cliente"}, SECRET, algorithm="HS256"),
        "sem sub": jwt.encode({"role": "cliente", "exp": agora + 600}, SECRET, algorithm="HS256"),
        "role service_role": jwt.encode({"sub": "x", "role": "service_role", "exp": agora + 600}, SECRET, algorithm="HS256"),
        "role anon": jwt.encode({"sub": "x", "role": "anon", "exp": agora + 600}, SECRET, algorithm="HS256"),
        "role inventado": jwt.encode({"sub": "x", "role": "root", "exp": agora + 600}, SECRET, algorithm="HS256"),
        "lixo": "abc.def.ghi",
    }
    for nome, tok in candidatos.items():
        r = client.get("/me", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 401, f"{nome}: {r.status_code}"


def test_user_metadata_nao_eleva_perfil(client):
    """O usuário edita user_metadata; só app_metadata.role (ou claim role assinada) vale."""
    tok = jwt.encode({"sub": "x", "role": "authenticated", "user_metadata": {"role": "gestor"}, "exp": int(time.time()) + 600},
                     SECRET, algorithm="HS256")
    assert client.get("/me", headers={"Authorization": f"Bearer {tok}"}).json()["role"] == "cliente"


def test_hs256_desligado_sem_jwt_secret(client, monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "")  # como na nuvem
    assert client.get("/me", headers=make_token("x", "gestor")).status_code == 401


# ---------- autorização (RN02 / IDOR / escalada) ----------
def test_cliente_nao_acessa_dados_de_outro_cliente(client, cliente, outro_cliente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    t = client.post("/tickets", json={"customer_id": cid, "categoria": "ATRASO", "prioridade": "ALTA", "assunto": "teste", "mensagem": "x"},
                    headers=cliente).json()["id"]
    sin = client.post("/claims", json={"order_id": oid, "tipo": "AVARIA", "descricao": "caixa", "valor_reclamado": "10.00"},
                      headers=cliente).json()["id"]
    alvos = [f"/customers/{cid}", f"/orders/{oid}", f"/orders/{oid}/tracking", f"/orders/{oid}/squads", f"/tickets/{t}", f"/claims/{sin}"]
    for a in alvos:
        assert client.get(a, headers=outro_cliente).status_code in (403, 404), a
    assert client.get("/orders", headers=outro_cliente).json() == []
    assert client.get("/tickets", headers=outro_cliente).json() == []
    assert client.get(f"/orders?customer_id={cid}", headers=outro_cliente).json() == []  # filtro não fura a RN02
    assert client.post(f"/tickets/{t}/messages", json={"mensagem": "invasor"}, headers=outro_cliente).status_code in (403, 404)
    assert client.post("/quotes", json={"customer_id": cid, "origem": "AA", "destino": "BB", "peso_kg": 1, "volume_m3": 1},
                       headers=outro_cliente).status_code in (403, 404)


def test_cliente_nao_executa_acoes_de_equipe(client, cliente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    t = client.post("/tickets", json={"customer_id": cid, "categoria": "ATRASO", "prioridade": "ALTA", "assunto": "teste", "mensagem": "x"},
                    headers=cliente).json()["id"]
    assert client.patch(f"/orders/{oid}/status", json={"status": "ENTREGUE"}, headers=cliente).status_code == 403
    assert client.patch(f"/tickets/{t}/status", json={"status": "RESOLVIDO"}, headers=cliente).status_code == 403
    assert client.put("/settings/integrations/wms", json={"base_url": "https://x.exemplo.com"}, headers=cliente).status_code == 403
    assert client.post("/settings/api-keys", json={"squad": "wms", "nome": "invasor"}, headers=cliente).status_code == 403
    assert client.post("/settings/integrations/wms/test", headers=cliente).status_code == 403


def test_mass_assignment_e_ignorado(client, cliente):
    r = client.post("/customers", json={"nome": "Loja X", "documento": "11222333000181", "tipo": "PJ", "email": "a@b.com",
                                        "owner_sub": "outra-pessoa", "id": "00000000-0000-0000-0000-000000000001"}, headers=cliente)
    assert r.status_code == 201
    assert r.json()["id"] != "00000000-0000-0000-0000-000000000001"
    assert "owner_sub" not in r.json() or r.json()["owner_sub"] == "user-cliente-1"


# ---------- entrada de dados ----------
PAYLOADS = ["' OR '1'='1", "'; DROP TABLE customers;--", "<script>alert(1)</script>", "${7*7}", "{{7*7}}", "../../etc/passwd",
            "\x00nulo", "A" * 5000, "😀" * 300, "%00%0d%0aSet-Cookie: x=1"]


def test_cotacao_com_valores_invalidos_nunca_da_500(client, cliente):
    cid = _criar_cliente(client, cliente)
    base = {"customer_id": cid, "origem": "São Paulo/SP", "destino": "Recife/PE", "peso_kg": 10, "volume_m3": 1}
    ruins = [{"peso_kg": -1}, {"peso_kg": 0}, {"peso_kg": 1e12}, {"peso_kg": "abc"}, {"peso_kg": None}, {"volume_m3": -5},
             {"peso_kg": float("inf")}, {"origem": ""}, {"origem": "A" * 201}, {"customer_id": "nao-e-uuid"}, {"customer_id": None}]
    for r in ruins:
        resp = client.post("/quotes", content=json.dumps({**base, **r}, allow_nan=True), headers={**cliente, "Content-Type": "application/json"})
        assert resp.status_code in (400, 403, 404, 422), f"{r}: {resp.status_code}"


def test_payloads_de_ataque_em_texto_nao_causam_erro_de_servidor(client, cliente):
    cid = _criar_cliente(client, cliente)
    for p in PAYLOADS:
        r1 = client.post("/tickets", json={"customer_id": cid, "categoria": "ATRASO", "prioridade": "MEDIA", "assunto": p[:200] or "xxx",
                                           "mensagem": p}, headers=cliente)
        assert r1.status_code in (201, 422), (p[:20], r1.status_code)
        r2 = client.post("/quotes", json={"customer_id": cid, "origem": p[:200] or "xx", "destino": "Recife/PE", "peso_kg": 1, "volume_m3": 1},
                         headers=cliente)
        assert r2.status_code in (201, 422), (p[:20], r2.status_code)
    # parâmetros de consulta
    for p in PAYLOADS[:4]:
        assert client.get("/orders", params={"status": p}, headers=cliente).status_code == 422
        assert client.get("/orders", params={"limit": p}, headers=cliente).status_code == 422
    assert client.get("/orders", params={"limit": 1000000}, headers=cliente).status_code == 422
    assert client.get("/orders", params={"offset": -1}, headers=cliente).status_code == 422
    assert client.get("/orders/nao-e-uuid", headers=cliente).status_code == 422
    # a tabela continua de pé depois das injeções
    assert client.get("/customers", headers=cliente).status_code == 200


def test_cpf_cnpj_invalido_e_barrado(client, cliente):
    for doc in ["123", "00000000000000", "11111111111", "abc", "11222333000182", "' OR 1=1"]:
        r = client.post("/customers", json={"nome": "Loja", "documento": doc, "tipo": "PJ", "email": "a@b.com"}, headers=cliente)
        assert r.status_code in (409, 422), (doc, r.status_code)


def test_textos_sem_limite_de_tamanho(client, cliente):
    """Mensagem de chamado e descrição de sinistro não podem aceitar megabytes (abuso de armazenamento/memória)."""
    cid = _criar_cliente(client, cliente)
    grande = "x" * 200_000
    r = client.post("/tickets", json={"customer_id": cid, "categoria": "ATRASO", "prioridade": "MEDIA", "assunto": "teste", "mensagem": grande},
                    headers=cliente)
    assert r.status_code == 422, f"mensagem de 200 KB aceita ({r.status_code})"


def test_corpo_gigante_e_recusado(client, cliente):
    r = client.post("/customers", content=b'{"nome": "' + b"A" * 2_000_000 + b'"}', headers={**cliente, "Content-Type": "application/json"})
    assert r.status_code in (413, 422), f"corpo de 2 MB aceito para validação ({r.status_code})"


# ---------- SSRF e integrações ----------
@pytest.mark.parametrize("alvo", ["http://169.254.169.254/latest/meta-data", "https://127.0.0.1", "https://localhost", "https://10.0.0.5",
                                  "https://192.168.1.1", "https://172.16.0.9", "https://[::1]", "https://0.0.0.0", "https://2130706433",
                                  "https://0x7f000001", "https://user:senha@exemplo.com", "ftp://exemplo.com", "file:///etc/passwd",
                                  "gopher://exemplo.com", "https://exemplo.com:22", "javascript:alert(1)", "//exemplo.com", "https://"])
def test_ssrf_urls_internas_sao_recusadas(alvo):
    with pytest.raises(Exception):  # noqa: B017 - qualquer recusa (DomainError) serve
        url_segura.validar_base_url(alvo, resolve=lambda h, p: ["10.0.0.1"] if h != "exemplo.com" else ["93.184.216.34"])


def test_rebinding_host_publico_que_resolve_para_ip_interno():
    with pytest.raises(Exception):  # noqa: B017
        url_segura.validar_base_url("https://parece-publico.exemplo.com", resolve=lambda h, p: ["127.0.0.1"])


def test_cabecalho_da_chave_nao_aceita_injecao(client, atendente):
    for h in ["X-Key\r\nX-Evil: 1", "X Key", "X-Key;x", "a" * 65, ""]:
        r = client.put("/settings/integrations/wms", json={"header_name": h}, headers=atendente)
        assert r.status_code == 422, (h, r.status_code)


# ---------- chaves de API emitidas pelo CRM ----------
def test_chave_da_nossa_api_so_le_pedidos(client, cliente, atendente):
    cid = _criar_cliente(client, cliente)
    _, oid = _pedido(client, cliente, cid)
    k = client.post("/settings/api-keys", json={"squad": "wms", "nome": "teste de segurança"}, headers=atendente).json()["chave"]
    h = {"X-API-Key": k}
    assert client.get("/orders", headers=h).status_code == 200
    proibidas = [("GET", "/customers"), ("GET", "/tickets"), ("GET", "/claims"), ("GET", "/settings/integrations"),
                 ("GET", "/settings/api-keys"), ("POST", "/settings/api-keys"), ("DELETE", f"/settings/api-keys/{oid}"),
                 ("PATCH", f"/orders/{oid}/status"), ("POST", "/orders"), ("GET", f"/orders/{oid}/tracking"), ("GET", f"/orders/{oid}/squads")]
    for m, rota in proibidas:
        r = client.request(m, rota, headers=h, json={} if m != "GET" else None)
        assert r.status_code in (401, 403, 404, 405, 422), f"{m} {rota}: {r.status_code}"
        assert r.status_code != 200, f"{m} {rota} aceitou a chave"


def test_chave_com_variacoes_e_negada(client, atendente):
    k = client.post("/settings/api-keys", json={"squad": "wms", "nome": "teste"}, headers=atendente).json()["chave"]
    for v in [k.upper(), k[:-1], k + "x", " " + k, k.replace("sk_", "SK_"), "sk_", "' OR '1'='1", ""]:
        r = client.get("/orders", headers={"X-API-Key": v})
        assert r.status_code == 401, v[:15]


# ---------- exposição de informação ----------
def test_erros_nao_vazam_detalhes_internos(client, cliente):
    for r in (client.get("/orders/00000000-0000-0000-0000-000000000000", headers=cliente), client.get("/rota-que-nao-existe")):
        corpo = r.text.lower()
        for sinal in ("traceback", "sqlalchemy", "psycopg", "/home/", "site-packages", "postgresql://"):
            assert sinal not in corpo


def test_metrics_nao_deve_ser_publico_quando_ha_token(client, monkeypatch):
    monkeypatch.setattr(settings, "metrics_token", "token-de-teste-1234")
    assert client.get("/metrics").status_code in (401, 403)
    assert client.get("/metrics", headers={"Authorization": "Bearer token-de-teste-1234"}).status_code == 200


def test_cors_nao_reflete_origem_nao_autorizada(client, monkeypatch):
    r = client.get("/health", headers={"Origin": "https://site-malicioso.example"})
    assert r.headers.get("access-control-allow-origin") in (None, "")
