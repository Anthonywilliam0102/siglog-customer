import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.domain.rules import FeedbackTarget, PedidoStatus, Prioridade, TicketStatus


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CustomerIn(BaseModel):
    nome: str = Field(min_length=2, max_length=200, examples=["Loja Exemplo Ltda"])
    documento: str = Field(examples=["11222333000181"], description="CPF (PF) ou CNPJ (PJ)")
    tipo: str = Field(pattern="^(PF|PJ)$", examples=["PJ"])
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["contato@exemplo.com"])
    telefone: str | None = None
    endereco: str | None = None
    owner_sub: str | None = Field(None, description="Somente equipe: id do usuário dono do cadastro")


class CustomerOut(Out):
    id: uuid.UUID
    nome: str
    documento: str
    tipo: str
    email: str
    telefone: str | None
    endereco: str | None
    created_at: datetime


class QuoteIn(BaseModel):
    customer_id: uuid.UUID
    origem: str = Field(min_length=2, max_length=200)
    destino: str = Field(min_length=2, max_length=200)
    peso_kg: float = Field(gt=0, le=100000)
    volume_m3: float = Field(gt=0, le=1000)


class QuoteOut(Out):
    id: uuid.UUID
    customer_id: uuid.UUID
    origem: str
    destino: str
    peso_kg: float
    volume_m3: float
    valor_estimado: Decimal
    expires_at: datetime


class OrderIn(BaseModel):
    quote_id: uuid.UUID


class OrderOut(Out):
    id: uuid.UUID
    customer_id: uuid.UUID
    quote_id: uuid.UUID
    status: PedidoStatus
    origem: str
    destino: str
    valor_estimado: Decimal
    created_at: datetime


class OrderStatusIn(BaseModel):
    status: PedidoStatus


class TrackingOut(BaseModel):
    order_id: str
    status: str
    events: list[dict] = []
    source: str = "tracking"  # "mock" quando o rastreamento é simulado (demo)


class TicketIn(BaseModel):
    customer_id: uuid.UUID
    order_id: uuid.UUID | None = None
    categoria: str = Field(min_length=2, max_length=50, examples=["ATRASO"])
    prioridade: Prioridade = Prioridade.MEDIA
    assunto: str = Field(min_length=3, max_length=200)
    mensagem: str = Field(min_length=1, max_length=5000)


class MessageIn(BaseModel):
    mensagem: str = Field(min_length=1, max_length=5000)


class MessageOut(Out):
    id: uuid.UUID
    author_role: str
    mensagem: str
    created_at: datetime


class TicketOut(Out):
    id: uuid.UUID
    customer_id: uuid.UUID
    order_id: uuid.UUID | None
    categoria: str
    prioridade: Prioridade
    assunto: str
    status: TicketStatus
    sla_due_at: datetime
    created_at: datetime


class TicketDetailOut(TicketOut):
    messages: list[MessageOut] = []


class TicketStatusIn(BaseModel):
    status: TicketStatus


class ClaimIn(BaseModel):
    order_id: uuid.UUID
    tipo: str = Field(min_length=2, max_length=30, examples=["AVARIA"])
    descricao: str = Field(min_length=3, max_length=5000)
    valor_reclamado: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class ClaimOut(Out):
    id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    tipo: str
    descricao: str
    valor_reclamado: Decimal
    status: str
    created_at: datetime


class FeedbackIn(BaseModel):
    target: FeedbackTarget
    nota: int = Field(ge=1, le=5)
    comentario: str | None = Field(None, max_length=2000)
    order_id: uuid.UUID | None = None
    ticket_id: uuid.UUID | None = None


class FeedbackOut(Out):
    id: uuid.UUID
    target: FeedbackTarget
    nota: int
    comentario: str | None
    order_id: uuid.UUID | None
    ticket_id: uuid.UUID | None


class MeOut(BaseModel):
    sub: str
    role: str


class IntegracaoOut(BaseModel):
    squad: str
    nome: str
    base_url: str | None
    header_name: str
    tem_chave: bool = Field(description="Indica se há chave guardada. O valor NUNCA é devolvido.")
    atualizado_em: datetime | None
    atualizado_por: str | None


class IntegracaoIn(BaseModel):
    base_url: str | None = Field(None, max_length=300, description="https://... (vazio remove)", examples=["https://tracking.exemplo.com"])
    header_name: str | None = Field(None, pattern=r"^[A-Za-z0-9-]{1,64}$", examples=["X-API-Key"])
    api_key: str | None = Field(None, min_length=8, max_length=512, description="Guardada cifrada; não é devolvida")
    limpar_chave: bool = False


class IntegracaoStatusOut(BaseModel):
    squad: str
    nome: str
    funcao: str
    modo: str = Field(description="configurada | simulada | nao_configurada")


class DetalheOut(BaseModel):
    rotulo: str
    valor: str


class PainelSquadOut(BaseModel):
    squad: str
    titulo: str
    fonte: str = Field(description="integracao | simulado | indisponivel | nao_configurada")
    status: str | None
    detalhes: list[DetalheOut] = []
    mensagem: str | None = None


class TesteIntegracaoOut(BaseModel):
    ok: bool
    status_http: int | None
    ms: int
    erro: str | None


class ChaveApiIn(BaseModel):
    squad: str = Field(examples=["wms"])
    nome: str = Field(min_length=3, max_length=80, examples=["Integração do WMS (produção)"])


class ChaveApiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    squad: str
    nome: str
    prefixo: str
    created_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None


class ChaveApiCriadaOut(ChaveApiOut):
    chave: str = Field(description="Aparece UMA única vez; guarde agora")
