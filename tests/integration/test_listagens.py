from tests.integration.test_fluxo_api import CLIENTE, _criar_cliente, _pedido

CLIENTE_2 = {"nome": "Maria Souza", "documento": "52998224725", "tipo": "PF", "email": "maria@exemplo.com"}


def _setup(client, cliente, outro_cliente):
    c1 = _criar_cliente(client, cliente)
    c2 = client.post("/customers", json=CLIENTE_2, headers=outro_cliente).json()["id"]
    _, o1 = _pedido(client, cliente, c1)
    _, o2 = _pedido(client, outro_cliente, c2)
    return c1, c2, o1, o2


def test_me_devolve_sub_e_perfil(client, cliente, atendente):
    assert client.get("/me", headers=cliente).json() == {"sub": "user-cliente-1", "role": "cliente"}
    assert client.get("/me", headers=atendente).json()["role"] == "atendente"
    assert client.get("/me").status_code == 401


def test_listagens_respeitam_rn02(client, cliente, outro_cliente, atendente):
    c1, c2, o1, o2 = _setup(client, cliente, outro_cliente)
    client.post("/tickets", json={"customer_id": c1, "categoria": "DUVIDA", "assunto": "Dúvida", "mensagem": "Oi"},
                headers=cliente)
    client.post("/tickets", json={"customer_id": c2, "categoria": "DUVIDA", "assunto": "Outra", "mensagem": "Oi"},
                headers=outro_cliente)
    client.post("/claims", json={"order_id": o1, "tipo": "AVARIA", "descricao": "xxx", "valor_reclamado": "10"},
                headers=cliente)

    assert [c["id"] for c in client.get("/customers", headers=cliente).json()] == [c1]
    assert [o["id"] for o in client.get("/orders", headers=cliente).json()] == [o1]
    assert [o["id"] for o in client.get("/orders", headers=outro_cliente).json()] == [o2]
    assert len(client.get("/tickets", headers=cliente).json()) == 1
    assert len(client.get("/claims", headers=cliente).json()) == 1
    assert client.get("/claims", headers=outro_cliente).json() == []

    # equipe vê tudo
    assert {o["id"] for o in client.get("/orders", headers=atendente).json()} == {o1, o2}
    assert len(client.get("/customers", headers=atendente).json()) == 2
    assert len(client.get("/tickets", headers=atendente).json()) == 2


def test_filtros_e_paginacao(client, cliente, outro_cliente, atendente):
    c1, c2, o1, o2 = _setup(client, cliente, outro_cliente)
    client.patch(f"/orders/{o1}/status", json={"status": "EM_SEPARACAO"}, headers=atendente)

    em_sep = client.get("/orders?status=EM_SEPARACAO", headers=atendente).json()
    assert [o["id"] for o in em_sep] == [o1]
    assert [o["id"] for o in client.get(f"/orders?customer_id={c2}", headers=atendente).json()] == [o2]
    assert len(client.get("/orders?limit=1", headers=atendente).json()) == 1
    assert len(client.get("/orders?limit=1&offset=1", headers=atendente).json()) == 1
    assert client.get("/orders?limit=1&offset=2", headers=atendente).json() == []


def test_parametros_invalidos_retornam_422(client, cliente):
    for qs in ("limit=0", "limit=101", "offset=-1", "status=INEXISTENTE"):
        assert client.get(f"/orders?{qs}", headers=cliente).status_code == 422


def test_cliente_nao_ve_pedidos_de_outro_mesmo_filtrando_por_customer_id(client, cliente, outro_cliente):
    c1, c2, o1, o2 = _setup(client, cliente, outro_cliente)
    assert client.get(f"/orders?customer_id={c2}", headers=cliente).json() == []
    assert CLIENTE["documento"]
