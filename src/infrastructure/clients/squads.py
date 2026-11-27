"""Camada anticorrupção (ACL) para os squads WMS e Financeiro: traduz o que eles respondem para o que o CRM mostra.

PENDENTE DE ALINHAMENTO: os caminhos e campos abaixo são uma PROPOSTA do Squad 06
(ver contracts/consumed/wms e contracts/consumed/financeiro) até os contratos oficiais chegarem.
"""
from datetime import timedelta

import httpx

SQUADS_COM_PAINEL = {
    "wms": {"titulo": "Separação no CD (WMS)", "caminho": "/separacao/pedidos/{order_id}"},
    "financeiro": {"titulo": "Cobrança e frete (Financeiro)", "caminho": "/cobrancas/pedidos/{order_id}"},
}

ROTULO_STATUS = {
    "wms": {"AGUARDANDO": "Aguardando separação", "EM_SEPARACAO": "Em separação", "SEPARADO": "Separado",
            "ENVIADO": "Enviado ao transporte", "CANCELADO": "Cancelado"},
    "financeiro": {"PENDENTE": "Cobrança pendente", "PAGA": "Paga", "VENCIDA": "Vencida", "ESTORNADA": "Estornada"},
}


def painel(squad: str, fonte: str, status: str | None = None, detalhes: list | None = None, mensagem: str | None = None) -> dict:
    return {"squad": squad, "titulo": SQUADS_COM_PAINEL[squad]["titulo"], "fonte": fonte, "status": status,
            "detalhes": detalhes or [], "mensagem": mensagem}


def _brl(v) -> str:
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _traduzir(squad: str, raw: dict, fonte: str) -> dict:
    status = ROTULO_STATUS[squad].get(str(raw.get("status", "")), str(raw.get("status", "Desconhecido")))
    if squad == "wms":
        det = []
        if raw.get("itens_total") is not None:
            det.append({"rotulo": "Itens separados", "valor": f"{raw.get('itens_separados', 0)} de {raw['itens_total']}"})
        if raw.get("atualizado_em"):
            det.append({"rotulo": "Atualizado em", "valor": raw["atualizado_em"]})
    else:
        det = []
        if raw.get("valor") is not None:
            det.append({"rotulo": "Valor", "valor": _brl(raw["valor"])})
        if raw.get("vencimento"):
            det.append({"rotulo": "Vencimento", "valor": raw["vencimento"]})
    return painel(squad, fonte, status, det)


def fetch_painel(squad: str, order_id: str, base_url: str, headers: dict | None = None) -> dict:
    caminho = SQUADS_COM_PAINEL[squad]["caminho"].format(order_id=order_id)
    try:
        r = httpx.get(f"{base_url}{caminho}", timeout=3.0, headers=headers or {}, follow_redirects=False)
        r.raise_for_status()
        raw = r.json()
    except (httpx.HTTPError, ValueError):
        return painel(squad, "indisponivel", mensagem="O serviço deste squad está indisponível no momento.")
    return _traduzir(squad, raw, "integracao")


def mock_painel(squad: str, order) -> dict:
    """Dados SIMULADOS (demonstração) derivados do status do pedido."""
    st = str(order.status)
    if squad == "wms":
        por_status = {"CRIADO": ("AGUARDANDO", 0), "EM_SEPARACAO": ("EM_SEPARACAO", 3), "EM_TRANSPORTE": ("ENVIADO", 5),
                      "ENTREGUE": ("ENVIADO", 5), "CANCELADO": ("CANCELADO", 0)}
        status_wms, separados = por_status[st]
        atualizado = order.updated_at.strftime("%d/%m/%Y %H:%M") if order.updated_at else None
        raw = {"status": status_wms, "itens_separados": separados, "itens_total": 5, "atualizado_em": atualizado}
    else:
        raw = {"status": {"ENTREGUE": "PAGA", "CANCELADO": "ESTORNADA"}.get(st, "PENDENTE"), "valor": str(order.valor_estimado),
               "vencimento": (order.created_at + timedelta(days=7)).strftime("%d/%m/%Y")}
    return _traduzir(squad, raw, "simulado")
