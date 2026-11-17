# Roteiro do Demoday (Release v1.0.0)

Deck: ver o artefato "SIG-Log Customer — Demoday" (11 slides; exportável em PPTX/PDF). Os resultados de carga do deck são **marcadores** até a execução do K6.

## Antes de apresentar (checklist)
- [ ] `docker compose up -d --build` sem erros (`docker compose ps -a`: api e worker *Up*, migrate *Exited (0)*)
- [ ] Tokens gerados: `python scripts/gen_token.py maria cliente` e `suporte1 atendente`
- [ ] Cliente e cotação de teste criados (plano B se a internet cair)
- [ ] Grafana aberto no dashboard *SIG-Log Customer*; Jaeger e RabbitMQ em abas
- [ ] K6 executado e tabela de `docs/13_load_test.md` + slide de carga preenchidos
- [ ] CI verde na `main` e tag `v1.0.0` criada

## Fluxo da demo (≈5 min)
1. Swagger (`/docs`) → Authorize com o token da maria.
2. `POST /customers` → `POST /quotes` (valor estimado, validade 24 h) → `POST /orders`.
3. RabbitMQ: exchange `siglog.events` recebeu `customer.pedido.criado`.
4. Mostrar RN02: token do `joao` em `GET /orders/{id}` → **403**.
5. Atendente altera status para `ENTREGUE` → cliente avalia a entrega (`POST /feedback`).
6. Grafana: clientes, tickets, satisfação; Jaeger: trace da requisição.

## Divisão sugerida de falas
Produto/UX (UI/UX) · Domínio e dados (Banco) · API, eventos e DevOps (Back) · Portal (Front) · perguntas técnicas: ATAM e ADRs (todos).
