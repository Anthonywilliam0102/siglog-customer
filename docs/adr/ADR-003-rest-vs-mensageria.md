# ADR-003 — REST vs mensageria
**Status:** Aceita

**Contexto:** O CRM precisa consultar dados (rastreamento) e propagar fatos (pedido criado, sinistro).
**Alternativas:** tudo REST síncrono; tudo mensageria; híbrido.
**Decisão:** Híbrido. **REST** para consultas/comandos do portal e consulta ao Tracking; **RabbitMQ** (exchange topic `siglog.events`) para eventos de domínio, com **Outbox** para publicação confiável.
**Justificativa:** eventos desacoplam WMS/Financeiro do CRM e toleram indisponibilidade deles; consultas precisam de resposta imediata.
**Consequências:** entrega at-least-once → consumidores idempotentes por `event_id`; operar um broker; latência eventual na propagação. Kafka foi descartado (RabbitMQ é o exigido no Project Kit).
