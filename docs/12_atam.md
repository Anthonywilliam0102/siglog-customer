# ATAM — Avaliação Arquitetural

Atributos de qualidade priorizados: **desempenho, disponibilidade, segurança, escalabilidade**.

## Cenário 1 — Performance: aumento repentino de requisições
- **Estímulo:** pico de 500 req/s no portal (campanha, fim de mês).
- **Decisão:** API stateless (FastAPI/uvicorn), escrita de eventos via Outbox (não bloqueia a resposta esperando o broker), consultas indexadas por `customer_id`.
- **Benefício:** processo escala horizontalmente; latência da API independe do RabbitMQ.
- **Custo:** o `POST` faz mais uma escrita (outbox) na transação.
- **Trade-off:** eventos chegam com atraso de ~1 s (polling do worker) em troca de resiliência. Validação: teste K6 (docs/13_load_test.md) — **PENDENTE**.

## Cenário 2 — Disponibilidade: dependência externa indisponível
- **Estímulo:** Tracking fora do ar; ou RabbitMQ fora do ar.
- **Decisão:** Tracking consultado com timeout de 3 s e erro controlado (503), sem afetar o restante do portal. RabbitMQ: eventos ficam no Outbox e são publicados quando o broker volta (worker com `connect_robust`).
- **Benefício:** falha isolada; nenhum pedido ou sinistro é perdido.
- **Custo:** consumidores veem eventos atrasados; Outbox cresce durante a queda.
- **Trade-off:** consistência eventual × disponibilidade. Falta: circuit breaker e cache de último status do rastreamento (melhoria futura).

## Cenário 3 — Segurança: usuário não autorizado tenta acessar dados
- **Estímulo:** cliente A requisita pedido do cliente B, ou token ausente/forjado.
- **Decisão:** JWT validado em toda rota; autorização por dono do recurso (RN02) na camada de aplicação; segredos fora do código.
- **Benefício:** vazamento entre clientes bloqueado (403), coberto por teste automatizado.
- **Custo:** consulta ao dono em cada requisição; HS256 exige proteger o segredo compartilhado.
- **Trade-off:** simplicidade (HS256) × robustez (RS256/JWKS, mais complexo). Ver ADR-005.

## Cenário 4 — Escalabilidade: volume de transações aumenta significativamente
- **Estímulo:** 10× mais pedidos/tickets.
- **Decisão:** serviço stateless atrás de load balancer; banco com índices; worker do Outbox usa `FOR UPDATE SKIP LOCKED` (permite várias instâncias sem duplicar); Database-per-Service.
- **Benefício:** escala horizontal de API e worker independentemente.
- **Custo:** operar múltiplas réplicas e pool de conexões; mais carga no Postgres.
- **Trade-off:** o banco único do serviço é o gargalo final (réplica de leitura/particionamento exigiria mais complexidade). Métricas de domínio lidas do banco no scrape devem virar contadores se o volume crescer.

## Riscos e pontos sensíveis
| Item | Tipo |
|---|---|
| Banco como ponto único do serviço | Risco |
| Eventos at-least-once exigem consumidores idempotentes | Ponto sensível |
| Dependência do contrato do Tracking ainda não publicado | Risco |
