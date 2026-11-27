# Squad 03 — Rastreamento de Cargas & Telemetria IoT

**Status do contrato:** ⏳ PENDENTE (aguardando o squad entregar)
**Responsável no squad:** [nome]  ·  **Última atualização:** [data]

## Relação com o CRM (Squad 06)
Nós CONSUMIMOS o rastreamento (REST) e o status de entrega (eventos). Usamos hoje uma **proposta nossa** (`openapi.yaml`), a ser substituída pelo contrato oficial.

Eventos nossos que interessam a este squad (ver `contracts/provided/`): —

## O que este squad deve entregar nesta pasta (por Pull Request)
| Arquivo | Conteúdo | Obrigatório |
|---|---|---|
| `openapi.yaml` | API REST do squad (endpoints, request/response, erros, exemplos), OpenAPI 3.x | se oferece REST |
| `asyncapi.yaml` **ou** `events.md` | eventos que o squad publica: nome, routing key, payload (JSON Schema) e exemplo | se publica eventos |
| `exemplos/*.json` | exemplos reais de request/response/evento | recomendado |
| `CONTATO.md` | quem responde por este contrato e como falar | recomendado |

## Como nós consumimos
- [ ] Contrato recebido e validado (`python scripts/validar_contratos.py`)
- [ ] Mock local ligado (`docker-compose.integracao.yml`)
- [ ] Teste de contrato escrito em `tests/contract/`
- [ ] Integração testada contra o ambiente real do squad

## Decisões pendentes
- [ ] Nomes de filas/routing keys e payloads alinhados
- [ ] Autenticação entre serviços definida (ver `docs/20_integracao_squads.md`)
