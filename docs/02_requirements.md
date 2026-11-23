# Requisitos

## Requisitos Funcionais
| ID | Requisito | UC | Prioridade |
|---|---|---|---|
| RF01 | Cadastrar cliente (PF/PJ) com validação de documento | UC01 | Alta |
| RF02 | Solicitar cotação informando origem, destino, peso/volume | UC02 | Alta |
| RF03 | Criar pedido a partir de cotação aceita | UC03 | Alta |
| RF04 | Consultar pedido (status, itens, datas) | UC04 | Alta |
| RF05 | Consultar rastreamento do pedido (via contrato do Tracking) | UC05 | Média |
| RF06 | Abrir atendimento/ticket com categoria e prioridade | UC06 | Alta |
| RF07 | Registrar sinistro/avaria vinculado a um pedido | UC07 | Alta |
| RF08 | Consultar sinistro e seu andamento | UC08 | Média |
| RF09 | Avaliar atendimento (nota 1–5 + comentário) | UC09 | Média |
| RF10 | Avaliar entrega (nota 1–5 + comentário) | UC10 | Média |
| RF11 | Publicar eventos de domínio (A.5) de forma confiável (outbox) | — | Alta |
| RF12 | Notificar cliente nas mudanças relevantes (`ClienteNotificado`) | — | Baixa |
| RF13 | Autenticação e perfis: cliente, atendente, gestor | — | Alta |

## Requisitos Não Funcionais
| ID | Requisito |
|---|---|
| RNF01 | Documentação OpenAPI 3 publicada e respeitada pelos consumidores |
| RNF02 | Logs JSON estruturados; métricas Prometheus; traces OpenTelemetry → Jaeger |
| RNF03 | Latência p95 < 500 ms em 100 req/s; taxa de erros < 1% (a validar no K6) |
| RNF04 | Banco isolado (Database-per-Service, PostgreSQL) |
| RNF05 | Segredos fora do código; dados pessoais minimizados e fictícios |
| RNF06 | Execução com `docker compose up`; CI com lint, testes, scan (Trivy) |
| RNF07 | Idempotência no consumo de eventos |
| RNF08 | Acessibilidade básica no portal (WCAG AA como meta) |

## Regras de negócio (propostas)
- RN01: pedido só pode ser criado a partir de cotação **válida e não expirada** (validade 24h).
- RN02: cliente só vê seus próprios pedidos, tickets e sinistros.
- RN03: sinistro exige pedido existente do mesmo cliente.
- RN04: avaliação de entrega só após pedido **entregue**; uma avaliação por pedido.
- RN05: ticket tem SLA por prioridade (ex.: alta 4h, média 24h, baixa 72h).
- RN06: pedido cancelado não aceita novo sinistro de transporte.
- RN07: o pedido segue CRIADO → EM_SEPARACAO → EM_TRANSPORTE → ENTREGUE; pode ser CANCELADO apenas antes do transporte; ENTREGUE e CANCELADO são finais. Repetir o mesmo status é idempotente (não notifica de novo).
