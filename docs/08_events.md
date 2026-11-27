# Catálogo de Eventos — SIG-Log Customer

> **Fonte verificada por máquina:** `contracts/provided/` (JSON Schema, exemplos e AsyncAPI, gerados do código e testados). Este arquivo é o resumo legível. Guia de integração: [docs/20_integracao_squads.md](20_integracao_squads.md).

**Broker:** RabbitMQ · **Exchange:** `siglog.events` (topic) · **Routing key:** `customer.<evento>` · **Formato:** JSON (envelope abaixo) · **Entrega:** at-least-once via *Outbox* → consumidores devem ser **idempotentes** (usar `event_id`).

## Envelope
```json
{
  "event_id": "uuid",
  "event_type": "PedidoCriado",
  "version": 1,
  "occurred_at": "2026-11-16T12:00:00Z",
  "producer": "siglog-customer",
  "correlation_id": "uuid",
  "data": { }
}
```

## Eventos publicados (Anexo A.5)
| Evento | Routing key | Consumidores | Payload (`data`) |
|---|---|---|---|
| CotacaoSolicitada | `customer.cotacao.solicitada` | Financeiro (opcional) | cotacao_id, cliente_id, origem, destino, peso_kg, volume_m3 |
| PedidoCriado | `customer.pedido.criado` | **WMS**, **Financeiro** | pedido_id, cliente_id, cotacao_id, origem, destino, carga{peso_kg,volume_m3}, valor_estimado |
| ChamadoAberto | `customer.chamado.aberto` | (interno / dashboards) | ticket_id, cliente_id, pedido_id?, categoria, prioridade |
| SinistroRegistrado | `customer.sinistro.registrado` | **Financeiro** | sinistro_id, pedido_id, cliente_id, tipo, valor_reclamado |
| EntregaAvaliada | `customer.entrega.avaliada` | Frota/Tracking (indicadores) | pedido_id, cliente_id, nota |
| ClienteNotificado | `customer.cliente.notificado` | (auditoria) | cliente_id, canal, motivo |

## Eventos consumidos (PROPOSTOS — alinhar com os squads)
| Evento | Produtor | Uso |
|---|---|---|
| EntregaConcluida / StatusRastreamentoAtualizado | Tracking | atualizar status do pedido; habilitar avaliação (RN04) |
| CobrancaGerada / FreteCalculado | Financeiro | exibir valor ao cliente |

> **PENDENTE DE ALINHAMENTO:** nomes/payloads dos eventos consumidos dependem dos outros squads.
