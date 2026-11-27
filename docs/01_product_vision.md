# Visão do Produto — Project Charter

## Produto
**SIG-Log Customer** — CRM, SAC & Portal do Cliente do ecossistema SIG-Log (Sistema de Informações Gerenciais de Logística Multimodal). É a **interface única de relacionamento** entre o cliente e a plataforma.

## Problema
Clientes de uma grande empresa logística nacional precisam cotar fretes, criar pedidos, acompanhar entregas, abrir chamados, registrar sinistros/avarias e avaliar o serviço. Hoje esses fluxos tendem a ficar espalhados em canais distintos (telefone, e-mail, planilhas), gerando retrabalho, baixa visibilidade e SLA difícil de medir.

## Objetivo
Oferecer autoatendimento em um portal e um CRM/SAC que registre e propague eventos para os demais módulos (WMS, Frota, Tracking, Financeiro, RH).

## Objetivos mensuráveis (propostos)
| Objetivo | Indicador |
|---|---|
| Reduzir esforço de atendimento | % de pedidos criados sem intervenção humana |
| Cumprir SLA de SAC | % de tickets respondidos dentro do SLA |
| Tratar sinistros com rapidez | Tempo médio entre registro e decisão |
| Medir satisfação | Nota média de entrega/atendimento (1–5) |
| Confiabilidade | Disponibilidade ≥ 99% na demo; p95 < 500 ms em carga normal |

## Escopo (dentro)
Cadastro de cliente, cotação, pedido, consulta de pedido/rastreamento, tickets de atendimento, sinistros, avaliações, notificações ao cliente (UC01–UC10).

## Fora do escopo
Separação/estoque (WMS), roteirização (Frota), telemetria IoT (Tracking), cálculo de frete e cobrança (Financeiro), jornada de motoristas (RH). Este módulo apenas **publica/consome eventos e consulta contratos** desses módulos.

## Papel na plataforma
Porta de entrada: o `PedidoCriado` dispara o fluxo em WMS e Financeiro; o `SinistroRegistrado` é consumido pelo Financeiro (estornos/indenizações).

## Equipe (4 pessoas)
Banco de dados · Back-end · Front-end · UI/UX.

## Premissas e riscos
- Outros squads podem atrasar contratos → usar **mocks** do OpenAPI.
- Projeto acadêmico: **somente dados fictícios**.
- Free tiers (Supabase pausa por inatividade) → banco local em container para dev/CI.
