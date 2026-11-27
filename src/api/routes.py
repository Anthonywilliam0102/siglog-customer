import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api import schemas as s
from src.api.auth import get_actor
from src.application import services as svc
from src.application.services import Actor
from src.domain.rules import PedidoStatus, TicketStatus
from src.infrastructure.db import get_session

router = APIRouter()


def commit(session: Session, value):
    """Persiste ANTES de responder (ver infrastructure/db.py) e devolve o valor da rota."""
    session.commit()
    return value


ERR = {401: {"description": "Não autenticado"}, 403: {"description": "Acesso negado"},
       404: {"description": "Não encontrado"}, 422: {"description": "Regra de negócio/validação"}}


Limit = Query(50, ge=1, le=100, description="Itens por página (máx. 100)")
Offset = Query(0, ge=0, description="Itens a pular")


@router.get("/me", response_model=s.MeOut, tags=["sessão"], summary="Quem sou eu (perfil do token)",
            responses={401: {"description": "Não autenticado"}})
def get_me(actor: Actor = Depends(get_actor)):
    return {"sub": actor.sub, "role": actor.role}


@router.get("/customers", response_model=list[s.CustomerOut], tags=["clientes"], summary="Listar clientes", responses=ERR)
def list_customers(limit: int = Limit, offset: int = Offset, session: Session = Depends(get_session),
                   actor: Actor = Depends(get_actor)):
    return svc.listar_clientes(session, actor, limit, offset)


@router.get("/orders", response_model=list[s.OrderOut], tags=["pedidos"], summary="Listar pedidos", responses=ERR)
def list_orders(status: PedidoStatus | None = None, customer_id: uuid.UUID | None = None, limit: int = Limit,
                offset: int = Offset, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.listar_pedidos(session, actor, status, customer_id, limit, offset)


@router.get("/tickets", response_model=list[s.TicketOut], tags=["SAC"], summary="Listar tickets", responses=ERR)
def list_tickets(status: TicketStatus | None = None, limit: int = Limit, offset: int = Offset,
                 session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.listar_tickets(session, actor, status, limit, offset)


@router.get("/claims", response_model=list[s.ClaimOut], tags=["sinistros"], summary="Listar sinistros", responses=ERR)
def list_claims(limit: int = Limit, offset: int = Offset, session: Session = Depends(get_session),
                actor: Actor = Depends(get_actor)):
    return svc.listar_sinistros(session, actor, limit, offset)


@router.post("/customers", response_model=s.CustomerOut, status_code=201, tags=["clientes"],
             summary="UC01 – Cadastrar cliente", responses={**ERR, 409: {"description": "Documento já cadastrado"}})
def post_customer(body: s.CustomerIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.cadastrar_cliente(session, actor, **body.model_dump()))


@router.get("/customers/{customer_id}", response_model=s.CustomerOut, tags=["clientes"], responses=ERR)
def get_customer(customer_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.obter_cliente(session, actor, customer_id)


@router.post("/quotes", response_model=s.QuoteOut, status_code=201, tags=["cotações"],
             summary="UC02 – Solicitar cotação", responses=ERR)
def post_quote(body: s.QuoteIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.solicitar_cotacao(session, actor, **body.model_dump()))


@router.post("/orders", response_model=s.OrderOut, status_code=201, tags=["pedidos"],
             summary="UC03 – Criar pedido a partir de cotação", responses={**ERR, 409: {"description": "Cotação já usada"}})
def post_order(body: s.OrderIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.criar_pedido(session, actor, body.quote_id))


@router.get("/orders/{order_id}", response_model=s.OrderOut, tags=["pedidos"],
            summary="UC04 – Consultar pedido", responses=ERR)
def get_order(order_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.consultar_pedido(session, actor, order_id)


@router.get("/orders/{order_id}/tracking", response_model=s.TrackingOut, tags=["pedidos"],
            summary="UC05 – Consultar rastreamento", responses={**ERR, 503: {"description": "Tracking indisponível"}})
def get_tracking(order_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.consultar_rastreamento(session, actor, order_id)


@router.patch("/orders/{order_id}/status", response_model=s.OrderOut, tags=["pedidos"],
              summary="(Equipe) Atualizar status do pedido", responses=ERR)
def patch_order_status(order_id: uuid.UUID, body: s.OrderStatusIn, session: Session = Depends(get_session),
                       actor: Actor = Depends(get_actor)):
    return commit(session, svc.atualizar_status_pedido(session, actor, order_id, body.status))


@router.post("/tickets", response_model=s.TicketOut, status_code=201, tags=["SAC"],
             summary="UC06 – Abrir atendimento", responses=ERR)
def post_ticket(body: s.TicketIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.abrir_ticket(session, actor, **body.model_dump()))


@router.get("/tickets/{ticket_id}", response_model=s.TicketDetailOut, tags=["SAC"], responses=ERR)
def get_ticket(ticket_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    t, msgs = svc.consultar_ticket(session, actor, ticket_id)
    return s.TicketDetailOut.model_validate({**s.TicketOut.model_validate(t).model_dump(),
                                             "messages": [s.MessageOut.model_validate(x) for x in msgs]})


@router.post("/tickets/{ticket_id}/messages", response_model=s.TicketOut, status_code=201, tags=["SAC"],
             summary="Responder ticket", responses=ERR)
def post_ticket_message(ticket_id: uuid.UUID, body: s.MessageIn, session: Session = Depends(get_session),
                        actor: Actor = Depends(get_actor)):
    return commit(session, svc.responder_ticket(session, actor, ticket_id, body.mensagem))


@router.patch("/tickets/{ticket_id}/status", response_model=s.TicketOut, tags=["SAC"],
              summary="(Equipe) Atualizar status do ticket", responses=ERR)
def patch_ticket_status(ticket_id: uuid.UUID, body: s.TicketStatusIn, session: Session = Depends(get_session),
                        actor: Actor = Depends(get_actor)):
    return commit(session, svc.atualizar_status_ticket(session, actor, ticket_id, body.status))


@router.post("/claims", response_model=s.ClaimOut, status_code=201, tags=["sinistros"],
             summary="UC07 – Registrar sinistro", responses=ERR)
def post_claim(body: s.ClaimIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.registrar_sinistro(session, actor, **body.model_dump()))


@router.get("/claims/{claim_id}", response_model=s.ClaimOut, tags=["sinistros"],
            summary="UC08 – Consultar sinistro", responses=ERR)
def get_claim(claim_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.consultar_sinistro(session, actor, claim_id)


@router.post("/feedback", response_model=s.FeedbackOut, status_code=201, tags=["satisfação"],
             summary="UC09/UC10 – Avaliar atendimento ou entrega", responses={**ERR, 409: {"description": "Já avaliado"}})
def post_feedback(body: s.FeedbackIn, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return commit(session, svc.avaliar(session, actor, **body.model_dump()))


@router.get("/settings/integrations", response_model=list[s.IntegracaoOut], tags=["configurações"],
            summary="Integrações com outros squads (equipe)", responses=ERR)
def list_integrations(session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.listar_integracoes(session, actor)


@router.put("/settings/integrations/{squad}", response_model=s.IntegracaoOut, tags=["configurações"],
            summary="Salvar URL e chave de API de um squad (equipe)",
            responses={**ERR, 409: {"description": "SETTINGS_ENCRYPTION_KEY não configurada no servidor"}})
def put_integration(squad: str, body: s.IntegracaoIn, session: Session = Depends(get_session),
                    actor: Actor = Depends(get_actor)):
    salvo = svc.salvar_integracao(session, actor, squad, body.base_url, body.header_name, body.api_key, body.limpar_chave)
    return commit(session, salvo)


@router.get("/integrations/status", response_model=list[s.IntegracaoStatusOut], tags=["configurações"],
            summary="Modo de cada integração (qualquer usuário logado; sem URLs nem chaves)", responses=ERR)
def get_integrations_status(session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.status_integracoes(session, actor)


@router.get("/orders/{order_id}/squads", response_model=list[s.PainelSquadOut], tags=["pedidos"],
            summary="O que os outros squads informam sobre o pedido (WMS e Financeiro)", responses=ERR)
def get_order_squads(order_id: uuid.UUID, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.paineis_do_pedido(session, actor, order_id)


@router.post("/settings/integrations/{squad}/test", response_model=s.TesteIntegracaoOut, tags=["configurações"],
             summary="Testar a conexão com a URL configurada (equipe)", responses=ERR)
def post_integration_test(squad: str, session: Session = Depends(get_session), actor: Actor = Depends(get_actor)):
    return svc.testar_integracao(session, actor, squad)
