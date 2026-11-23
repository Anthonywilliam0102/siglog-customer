import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api import schemas as s
from src.api.auth import get_actor
from src.application import services as svc
from src.application.services import Actor
from src.infrastructure.db import get_session

router = APIRouter()


def commit(session: Session, value):
    """Persiste ANTES de responder (ver infrastructure/db.py) e devolve o valor da rota."""
    session.commit()
    return value


ERR = {401: {"description": "Não autenticado"}, 403: {"description": "Acesso negado"},
       404: {"description": "Não encontrado"}, 422: {"description": "Regra de negócio/validação"}}


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
