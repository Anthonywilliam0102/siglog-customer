"""Casos de uso UC01–UC10. A `Session` do SQLAlchemy atua como Unit of Work (ver ADR-001)."""
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.domain import events, rules
from src.domain.errors import Conflict, DomainError, Forbidden, NotFound
from src.domain.rules import FeedbackTarget, PedidoStatus, Prioridade, Role, TicketStatus
from src.infrastructure import models as m
from src.infrastructure.clients.tracking import fetch_tracking, mock_tracking
from src.infrastructure.clients.url_segura import validar_base_url
from src.infrastructure.segredos import cifrar, decifrar


@dataclass(frozen=True)
class Actor:
    sub: str
    role: Role

    @property
    def is_staff(self) -> bool:
        return self.role in rules.STAFF


# ---------- helpers ----------
def _emit(session: Session, event_type: str, data: dict) -> None:
    session.add(m.OutboxEvent(routing_key=events.ROUTING_KEYS[event_type],
                              payload=events.envelope(event_type, data)))


def _get(session: Session, model, id_: uuid.UUID, label: str):
    obj = session.get(model, id_)
    if obj is None:
        raise NotFound(f"{label} não encontrado(a)")
    return obj


def _flush_or_conflict(session: Session, message: str) -> None:
    """Flush que traduz violação de unique (corrida entre requisições) em 409."""
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise Conflict(message) from exc


def _customer_for(session: Session, actor: Actor, customer_id: uuid.UUID) -> m.Customer:
    """RN02: cliente só acessa os próprios dados; equipe acessa todos."""
    c = _get(session, m.Customer, customer_id, "Cliente")
    if not actor.is_staff and c.owner_sub != actor.sub:
        raise Forbidden("Acesso negado")
    return c


# ---------- UC01 ----------
def cadastrar_cliente(session: Session, actor: Actor, nome: str, documento: str, tipo: str,
                      email: str, telefone: str | None, endereco: str | None,
                      owner_sub: str | None = None) -> m.Customer:
    doc = rules.normalizar_documento(documento, tipo)
    if session.scalar(select(m.Customer).where(m.Customer.documento == doc)):
        raise Conflict("Já existe cliente com este documento")
    owner = owner_sub if (owner_sub and actor.is_staff) else actor.sub
    c = m.Customer(owner_sub=owner, nome=nome, documento=doc, tipo=tipo, email=email,
                   telefone=telefone, endereco=endereco)
    session.add(c)
    _flush_or_conflict(session, "Já existe cliente com este documento")
    return c


def obter_cliente(session: Session, actor: Actor, customer_id: uuid.UUID) -> m.Customer:
    return _customer_for(session, actor, customer_id)


# ---------- UC02 ----------
def solicitar_cotacao(session: Session, actor: Actor, customer_id: uuid.UUID, origem: str,
                      destino: str, peso_kg: float, volume_m3: float) -> m.Quote:
    _customer_for(session, actor, customer_id)
    q = m.Quote(customer_id=customer_id, origem=origem, destino=destino, peso_kg=peso_kg,
                volume_m3=volume_m3, valor_estimado=rules.estimar_valor(peso_kg, volume_m3),
                expires_at=rules.utcnow() + rules.COTACAO_VALIDADE)
    session.add(q)
    session.flush()
    _emit(session, "CotacaoSolicitada", {
        "cotacao_id": str(q.id), "cliente_id": str(customer_id), "origem": origem,
        "destino": destino, "peso_kg": peso_kg, "volume_m3": volume_m3})
    return q


# ---------- UC03 ----------
def criar_pedido(session: Session, actor: Actor, quote_id: uuid.UUID) -> m.Order:
    q = session.get(m.Quote, quote_id, with_for_update=True)  # trava a cotação contra pedidos simultâneos
    if q is None:
        raise NotFound("Cotação não encontrada")
    _customer_for(session, actor, q.customer_id)
    if q.accepted:
        raise Conflict("Cotação já utilizada em um pedido")
    if rules.cotacao_expirada(q.expires_at):  # RN01
        raise DomainError("Cotação expirada")
    o = m.Order(customer_id=q.customer_id, quote_id=q.id, origem=q.origem, destino=q.destino,
                valor_estimado=q.valor_estimado, status=PedidoStatus.CRIADO)
    q.accepted = True
    session.add(o)
    _flush_or_conflict(session, "Cotação já utilizada em um pedido")
    _emit(session, "PedidoCriado", {
        "pedido_id": str(o.id), "cliente_id": str(o.customer_id), "cotacao_id": str(q.id),
        "origem": o.origem, "destino": o.destino,
        "carga": {"peso_kg": q.peso_kg, "volume_m3": q.volume_m3},
        "valor_estimado": str(o.valor_estimado)})
    return o


# ---------- UC04 / UC05 ----------
def consultar_pedido(session: Session, actor: Actor, order_id: uuid.UUID) -> m.Order:
    o = _get(session, m.Order, order_id, "Pedido")
    _customer_for(session, actor, o.customer_id)
    return o


def consultar_rastreamento(session: Session, actor: Actor, order_id: uuid.UUID) -> dict:
    o = consultar_pedido(session, actor, order_id)
    cfg = session.get(m.IntegrationSetting, "tracking")
    base = cfg.base_url if cfg and cfg.base_url else None
    if base:  # integração configurada na tela de Configurações: tem prioridade sobre o simulado
        chave = decifrar(cfg.api_key_enc) if cfg.api_key_enc else None
        return fetch_tracking(str(o.id), base, {cfg.header_name: chave} if chave else None)
    if settings.tracking_mock and not settings.tracking_base_url:
        return mock_tracking(o)
    return fetch_tracking(str(o.id))


def atualizar_status_pedido(session: Session, actor: Actor, order_id: uuid.UUID,
                            status: PedidoStatus) -> m.Order:
    """Uso interno (equipe) até o consumidor de eventos do Tracking existir."""
    if not actor.is_staff:
        raise Forbidden("Apenas a equipe pode alterar o status")
    o = _get(session, m.Order, order_id, "Pedido")
    if status == o.status:
        return o  # idempotente: sem mudança, sem notificação
    if not rules.transicao_valida(o.status, status):
        raise DomainError(f"Transição de status inválida: {o.status} -> {status}")
    o.status = status
    _emit(session, "ClienteNotificado", {
        "cliente_id": str(o.customer_id), "canal": "email", "motivo": f"pedido {status}"})
    return o


# ---------- UC06 ----------
def abrir_ticket(session: Session, actor: Actor, customer_id: uuid.UUID, categoria: str,
                 prioridade: Prioridade, assunto: str, mensagem: str,
                 order_id: uuid.UUID | None = None) -> m.Ticket:
    _customer_for(session, actor, customer_id)
    if order_id:
        o = _get(session, m.Order, order_id, "Pedido")
        if o.customer_id != customer_id:
            raise Forbidden("Pedido não pertence ao cliente")
    t = m.Ticket(customer_id=customer_id, order_id=order_id, categoria=categoria,
                 prioridade=prioridade, assunto=assunto, sla_due_at=rules.sla_due(prioridade))
    session.add(t)
    session.flush()
    session.add(m.TicketMessage(ticket_id=t.id, author_sub=actor.sub, author_role=actor.role,
                                mensagem=mensagem))
    _emit(session, "ChamadoAberto", {
        "ticket_id": str(t.id), "cliente_id": str(customer_id),
        "pedido_id": str(order_id) if order_id else None,
        "categoria": categoria, "prioridade": prioridade})
    return t


def consultar_ticket(session: Session, actor: Actor, ticket_id: uuid.UUID) -> tuple[m.Ticket, list]:
    t = _get(session, m.Ticket, ticket_id, "Ticket")
    _customer_for(session, actor, t.customer_id)
    msgs = list(session.scalars(select(m.TicketMessage).where(m.TicketMessage.ticket_id == t.id)
                                .order_by(m.TicketMessage.created_at)))
    return t, msgs


def responder_ticket(session: Session, actor: Actor, ticket_id: uuid.UUID, mensagem: str) -> m.Ticket:
    t = _get(session, m.Ticket, ticket_id, "Ticket")
    _customer_for(session, actor, t.customer_id)
    if t.status == TicketStatus.RESOLVIDO:
        raise DomainError("Ticket resolvido não aceita novas mensagens")
    session.add(m.TicketMessage(ticket_id=t.id, author_sub=actor.sub, author_role=actor.role,
                                mensagem=mensagem))
    if actor.is_staff and t.status == TicketStatus.ABERTO:
        t.status = TicketStatus.EM_ATENDIMENTO
    return t


def atualizar_status_ticket(session: Session, actor: Actor, ticket_id: uuid.UUID,
                            status: TicketStatus) -> m.Ticket:
    if not actor.is_staff:
        raise Forbidden("Apenas a equipe pode alterar o status")
    t = _get(session, m.Ticket, ticket_id, "Ticket")
    t.status = status
    return t


# ---------- UC07 / UC08 ----------
def registrar_sinistro(session: Session, actor: Actor, order_id: uuid.UUID, tipo: str,
                       descricao: str, valor_reclamado) -> m.Claim:
    o = _get(session, m.Order, order_id, "Pedido")
    _customer_for(session, actor, o.customer_id)  # RN03
    if o.status == PedidoStatus.CANCELADO:  # RN06
        raise DomainError("Pedido cancelado não aceita sinistro")
    c = m.Claim(order_id=o.id, customer_id=o.customer_id, tipo=tipo, descricao=descricao,
                valor_reclamado=valor_reclamado)
    session.add(c)
    session.flush()
    _emit(session, "SinistroRegistrado", {
        "sinistro_id": str(c.id), "pedido_id": str(o.id), "cliente_id": str(o.customer_id),
        "tipo": tipo, "valor_reclamado": str(valor_reclamado)})
    return c


def consultar_sinistro(session: Session, actor: Actor, claim_id: uuid.UUID) -> m.Claim:
    c = _get(session, m.Claim, claim_id, "Sinistro")
    _customer_for(session, actor, c.customer_id)
    return c


# ---------- UC09 / UC10 ----------
def avaliar(session: Session, actor: Actor, target: FeedbackTarget, nota: int,
            comentario: str | None, order_id: uuid.UUID | None,
            ticket_id: uuid.UUID | None) -> m.Feedback:
    rules.validar_nota(nota)
    if target == FeedbackTarget.ENTREGA:
        if not order_id:
            raise DomainError("order_id é obrigatório para avaliar a entrega")
        o = _get(session, m.Order, order_id, "Pedido")
        _customer_for(session, actor, o.customer_id)
        if o.status != PedidoStatus.ENTREGUE:  # RN04
            raise DomainError("A entrega só pode ser avaliada após o pedido ser entregue")
        customer_id, ticket_id = o.customer_id, None
    else:
        if not ticket_id:
            raise DomainError("ticket_id é obrigatório para avaliar o atendimento")
        t = _get(session, m.Ticket, ticket_id, "Ticket")
        _customer_for(session, actor, t.customer_id)
        customer_id, order_id = t.customer_id, None
    f = m.Feedback(customer_id=customer_id, target=target, order_id=order_id,
                   ticket_id=ticket_id, nota=nota, comentario=comentario)
    session.add(f)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise Conflict("Este item já foi avaliado") from exc
    if target == FeedbackTarget.ENTREGA:
        _emit(session, "EntregaAvaliada", {
            "pedido_id": str(order_id), "cliente_id": str(customer_id), "nota": nota})
    return f


# ---------- listagens (portal e fila do atendimento) ----------
def _listar(session: Session, actor: Actor, model, *where, limit: int = 50, offset: int = 0):
    """RN02: cliente só enxerga o que pertence aos cadastros dele; equipe enxerga tudo."""
    stmt = select(model)
    if model is not m.Customer:
        stmt = stmt.join(m.Customer, m.Customer.id == model.customer_id)
    if not actor.is_staff:
        stmt = stmt.where(m.Customer.owner_sub == actor.sub)
    for cond in where:
        stmt = stmt.where(cond)
    return list(session.scalars(stmt.order_by(model.created_at.desc(), model.id).limit(limit).offset(offset)))


def listar_clientes(session: Session, actor: Actor, limit: int = 50, offset: int = 0):
    return _listar(session, actor, m.Customer, limit=limit, offset=offset)


def listar_pedidos(session: Session, actor: Actor, status: PedidoStatus | None = None,
                   customer_id: uuid.UUID | None = None, limit: int = 50, offset: int = 0):
    where = []
    if status:
        where.append(m.Order.status == status)
    if customer_id:
        where.append(m.Order.customer_id == customer_id)
    return _listar(session, actor, m.Order, *where, limit=limit, offset=offset)


def listar_tickets(session: Session, actor: Actor, status: TicketStatus | None = None,
                   limit: int = 50, offset: int = 0):
    where = [m.Ticket.status == status] if status else []
    return _listar(session, actor, m.Ticket, *where, limit=limit, offset=offset)


def listar_sinistros(session: Session, actor: Actor, limit: int = 50, offset: int = 0):
    return _listar(session, actor, m.Claim, limit=limit, offset=offset)


# ---------- integrações com outros squads (Configurações) ----------
SQUADS = {"wms": "Squad 01 · WMS & Estoque", "frota": "Squad 02 · Frota & Roteirização", "tracking": "Squad 03 · Rastreamento",
          "financeiro": "Squad 04 · Financeiro", "rh": "Squad 05 · RH & Jornada"}


def _so_equipe(actor: Actor) -> None:
    if not actor.is_staff:
        raise Forbidden("Apenas a equipe pode ver ou alterar as integrações")


def _integracao_out(squad: str, cfg: m.IntegrationSetting | None) -> dict:
    return {"squad": squad, "nome": SQUADS[squad], "base_url": cfg.base_url if cfg else None,
            "header_name": cfg.header_name if cfg else "X-API-Key", "tem_chave": bool(cfg and cfg.api_key_enc),
            "atualizado_em": cfg.updated_at if cfg else None, "atualizado_por": cfg.updated_by if cfg else None}


def listar_integracoes(session: Session, actor: Actor) -> list[dict]:
    _so_equipe(actor)
    existentes = {c.squad: c for c in session.scalars(select(m.IntegrationSetting))}
    return [_integracao_out(sq, existentes.get(sq)) for sq in SQUADS]


def salvar_integracao(session: Session, actor: Actor, squad: str, base_url: str | None, header_name: str | None,
                      api_key: str | None, limpar_chave: bool) -> dict:
    """A chave de API é cifrada e nunca devolvida. `base_url` vazio remove a URL (volta ao padrão do servidor)."""
    _so_equipe(actor)
    if squad not in SQUADS:
        raise NotFound("Squad não encontrado")
    cfg = session.get(m.IntegrationSetting, squad) or m.IntegrationSetting(squad=squad, header_name="X-API-Key")
    if base_url is not None:
        cfg.base_url = validar_base_url(base_url) if base_url.strip() else None
    if header_name:
        cfg.header_name = header_name
    if limpar_chave:
        cfg.api_key_enc = None
    if api_key:
        cfg.api_key_enc = cifrar(api_key)
    cfg.updated_by = actor.sub
    session.add(cfg)
    session.flush()
    return _integracao_out(squad, cfg)
