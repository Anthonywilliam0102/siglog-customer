# DDD — Domínio do SIG-Log Customer

## Event Storming (resumo)
**Eventos de domínio (laranja)**: `ClienteCadastrado`, `CotacaoSolicitada`, `CotacaoAceita`, `PedidoCriado`, `PedidoCancelado`, `ChamadoAberto`, `ChamadoResolvido`, `SinistroRegistrado`, `SinistroDecidido`, `AtendimentoAvaliado`, `EntregaAvaliada`, `ClienteNotificado`.

**Comandos (azul)**: CadastrarCliente, SolicitarCotacao, AceitarCotacao, CriarPedido, CancelarPedido, AbrirChamado, ResponderChamado, RegistrarSinistro, DecidirSinistro, AvaliarAtendimento, AvaliarEntrega.

**Atores**: Cliente, Atendente, Gestor. **Sistemas externos**: WMS, Financeiro, Tracking (eventos/contratos).

**Políticas (lilás)**
- Quando `PedidoCriado` → publicar para WMS e Financeiro.
- Quando `SinistroRegistrado` → publicar para Financeiro.
- Quando mudar status relevante → notificar cliente (`ClienteNotificado`).
- Quando ticket exceder SLA → alertar gestor (dashboard).

## Bounded Context
**Customer Relationship** (este serviço): cliente, cotação, pedido (visão do cliente), SAC, sinistro, satisfação.

**Linguagem ubíqua**: Cliente, Cotação, Pedido, Ticket, Atendimento, Sinistro, Avaliação, SLA.

## Agregados
| Agregado (raiz) | Contém | Invariantes |
|---|---|---|
| **Cliente** | documento, nome, contato, endereço | documento único e válido |
| **Cotacao** | origem, destino, carga, valor estimado, validade | expira em 24h; só aceita uma vez |
| **Pedido** | cotação de origem, status, itens | só nasce de cotação válida |
| **Ticket** | categoria, prioridade, SLA, **Atendimentos** (mensagens) | prioridade define SLA; fechado não recebe resposta |
| **Sinistro** | pedido, tipo, descrição, status, valor reclamado | pedido do mesmo cliente |
| **Avaliacao** | alvo (entrega/atendimento), nota, comentário | nota 1–5; uma por alvo (`Satisfacao` = agregação/indicador derivado) |

## Mapeamento Entidade → Agregado (Anexo A.3)
Cliente→Cliente · Cotacao→Cotacao · Pedido→Pedido · Ticket e Atendimento→Ticket · Sinistro→Sinistro · Avaliacao e Satisfacao→Avaliacao.
