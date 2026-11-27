# UX — Matriz CSD e Mapa de Empatia (RASCUNHO)

> **Status: hipóteses a validar.** Foram derivadas do domínio e das personas (`03_personas.md`), **não** de pesquisa com usuários.
> O UI/UX do squad deve confirmar com entrevistas reais (mesmo 3–5 pessoas) e marcar cada item como *confirmado* ou *descartado*.

## Matriz CSD (Certezas, Suposições, Dúvidas)
| Certezas (vêm do enunciado) | Suposições (a validar) | Dúvidas (perguntar) |
|---|---|---|
| O cliente precisa cotar, criar pedido, rastrear, abrir chamado, registrar sinistro e avaliar. | Clientes PJ preferem cotar em lote e acompanhar vários pedidos numa lista. | Qual o canal que o cliente usa hoje (telefone, e-mail, WhatsApp)? |
| O atendimento tem SLA por prioridade. | O cliente quer saber o status sem precisar ligar. | O cliente aceita abrir sinistro sem anexar foto? |
| Sinistro e avaria exigem registro vinculado a um pedido. | Linguagem simples importa mais que muitas opções (persona PF ocasional). | Que informação mínima é necessária para a cotação? |
| Cada cliente só pode ver os próprios dados. | Notificar por e-mail basta no início. | O cliente quer avaliar a entrega logo ao receber? |

## Mapa de Empatia — Marina Duarte (compradora de e-commerce, PJ)
| | |
|---|---|
| **Pensa e sente** | "Preciso saber onde está meu pedido." Ansiedade com atraso; medo de cliente final reclamar. |
| **Vê** | Pedidos em planilhas, e-mails de transportadoras, status que não batem. |
| **Ouve** | Cliente final cobrando; colegas dizendo que "ligar resolve mais rápido". |
| **Fala e faz** | Liga para o atendimento; cota em mais de uma transportadora; guarda comprovantes. |
| **Dores** | Falta de visibilidade, cotação demorada, difícil reportar avaria com evidência. |
| **Ganhos** | Cotar em segundos, ver o status em um lugar, resolver avaria sem telefonema. |

## Mapa de Empatia — Roberto Lima (atendente SAC)
| | |
|---|---|
| **Pensa e sente** | Pressão por SLA; frustração com informação espalhada. |
| **Vê** | Fila de chamados, vários sistemas abertos ao mesmo tempo. |
| **Ouve** | Cliente irritado; gestor cobrando prazo. |
| **Fala e faz** | Pergunta o número do pedido, busca em sistemas diferentes, escala casos. |
| **Dores** | Falta de histórico do cliente e do pedido em um lugar só. |
| **Ganhos** | Ver chamado, pedido e rastreamento juntos; priorizar pelo SLA. |

## Heurísticas de usabilidade a aplicar no portal (Nielsen)
Visibilidade do status (pedido e chamado sempre mostram o estado), mensagens de erro claras em português, prevenção de erro (validar CPF/CNPJ no formulário), consistência entre telas, reconhecimento em vez de memorização (listas dos próprios pedidos), acessibilidade (contraste, foco visível, rótulos nos campos).

## Pendente do UI/UX
- [ ] Entrevistar usuários e atualizar esta matriz
- [ ] Wireframes e protótipo no Figma (ou o próprio front como protótipo navegável)
- [ ] Teste de usabilidade com tarefas (cotar, criar pedido, abrir chamado) e registrar resultados reais
