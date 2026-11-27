import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.domain.rules import utcnow


class Base(DeclarativeBase):
    pass


def _id():
    return mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


def _now():
    return mapped_column(DateTime(timezone=True), default=utcnow)


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[uuid.UUID] = _id()
    owner_sub: Mapped[str] = mapped_column(String(128), index=True)
    nome: Mapped[str] = mapped_column(String(200))
    documento: Mapped[str] = mapped_column(String(14), unique=True)
    tipo: Mapped[str] = mapped_column(String(2))
    email: Mapped[str] = mapped_column(String(200))
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = _now()


class Quote(Base):
    __tablename__ = "quotes"
    id: Mapped[uuid.UUID] = _id()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    origem: Mapped[str] = mapped_column(String(200))
    destino: Mapped[str] = mapped_column(String(200))
    peso_kg: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float] = mapped_column(Float)
    valor_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = _now()


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = _id()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    quote_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quotes.id"), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="CRIADO")
    origem: Mapped[str] = mapped_column(String(200))
    destino: Mapped[str] = mapped_column(String(200))
    valor_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = _now()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[uuid.UUID] = _id()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    categoria: Mapped[str] = mapped_column(String(50))
    prioridade: Mapped[str] = mapped_column(String(10))
    assunto: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="ABERTO")
    sla_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()


class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id: Mapped[uuid.UUID] = _id()
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tickets.id"), index=True)
    author_sub: Mapped[str] = mapped_column(String(128))
    author_role: Mapped[str] = mapped_column(String(20))
    mensagem: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = _now()


class Claim(Base):
    __tablename__ = "claims"
    id: Mapped[uuid.UUID] = _id()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(30))
    descricao: Mapped[str] = mapped_column(Text)
    valor_reclamado: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default="REGISTRADO")
    created_at: Mapped[datetime] = _now()


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("order_id", "target", name="uq_feedback_order_target"),
        UniqueConstraint("ticket_id", "target", name="uq_feedback_ticket_target"),
    )
    id: Mapped[uuid.UUID] = _id()
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    target: Mapped[str] = mapped_column(String(15))
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("tickets.id"), nullable=True)
    nota: Mapped[int] = mapped_column(Integer)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = _now()


class OutboxEvent(Base):
    """Outbox: eventos gravados na mesma transação do negócio e publicados por um worker."""

    __tablename__ = "outbox_events"
    id: Mapped[uuid.UUID] = _id()
    routing_key: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = _now()
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)


class IntegrationSetting(Base):
    """Configuração de integração com outro squad (URL base e chave de API cifrada). Uma linha por squad."""

    __tablename__ = "integration_settings"
    squad: Mapped[str] = mapped_column(String(20), primary_key=True)
    base_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    header_name: Mapped[str] = mapped_column(String(64), default="X-API-Key")
    api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    updated_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
