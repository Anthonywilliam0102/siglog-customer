# Integração entre squads: como entregamos e como recebemos

O SIG-Log é **uma plataforma de 6 módulos**: ninguém é dono sozinho (Project Kit §20). Cada squad publica **contratos** (REST e eventos) e consome os dos outros. Aqui está como o Squad 06 (CRM) faz as duas mãos.

## 1. Mapa (squads inferidos da ordem do Project Kit; **confirmar com o professor**)
| Squad | Módulo | Relação com o CRM |
|---|---|---|
| 01 | WMS & Estoque/CD | **consome** `PedidoCriado` (iniciar separação) |
| 02 | Frota, Modais & Roteirização | sem integração direta; pode usar `EntregaAvaliada` |
| 03 | Rastreamento & Telemetria IoT | **nós consumimos**: rastreamento (REST) e status de entrega (evento) |
| 04 | Financeiro & Faturamento | **consome** `PedidoCriado` (frete/cobrança) e `SinistroRegistrado` (estorno) |
| 05 | RH, Jornada & Escalonamento | sem integração direta |
| 06 | **CRM, SAC & Portal (nós)** | porta de entrada: o pedido nasce aqui |

## 2. O que ENTREGAMOS (e onde está)
| Canal | Onde | Observação |
|---|---|---|
| **REST** | `openapi.yaml` + Swagger em `<URL-da-API>/docs` | autenticação: JWT (Supabase). Ver decisão de auth entre serviços (§5) |
| **Eventos** | `contracts/provided/events/*.schema.json`, `examples/`, `asyncapi.yaml` | exchange **`siglog.events`** (topic, durável); routing key `customer.<agregado>.<evento>` |
| Texto | `docs/08_events.md` | resumo legível |

Eventos publicados: `CotacaoSolicitada`, `PedidoCriado`, `ChamadoAberto`, `SinistroRegistrado`, `EntregaAvaliada`, `ClienteNotificado`.

**Garantias:** entrega *at-least-once* (Outbox) → **deduplicar por `event_id`**; envelope fixo (`event_id`, `event_type`, `version`, `occurred_at`, `producer`, `correlation_id`, `data`); mudanças incompatíveis sobem `version`.
**O contrato é verificado:** o CI falha se `contracts/provided/` ou `openapi.yaml` estiverem desatualizados em relação ao código, e um teste valida que os eventos **realmente emitidos** obedecem aos schemas.

**Como outro squad consome** (exemplo pronto, serve de modelo):
```bash
RABBITMQ_URL=amqp://usuario:senha@host:5672/ \
  python scripts/consumir_eventos.py --fila wms-pedidos --chave customer.pedido.criado
```
Cada squad cria **a sua fila** ligada ao exchange (não compartilhar fila). Ao receber: validar o schema, deduplicar por `event_id`, confirmar (ack) só depois de processar.

## 3. O que RECEBEMOS (e onde colocar)
Cada squad entrega o seu contrato **por Pull Request** na pasta dele: `contracts/consumed/<squad>/` (`openapi.yaml` e/ou `asyncapi.yaml`/`events.md`, exemplos, contato). O que não puder abrir PR envia os arquivos a quem do time commita. Cada pasta já tem um `README.md` com o que esperamos e o checklist.
1. **Validar:** `python scripts/validar_contratos.py` (o CI roda). Lista quem ainda não entregou.
2. **Mock:** `docker-compose.integracao.yml` sobe o Prism com o contrato da pasta `tracking/` (e de outros, quando houver).
3. **Teste de contrato:** escrever em `tests/contract/` (modelo: `test_tracking_consumido.py`), garantindo que nossa camada anticorrupção entende o contrato.
4. **Integrar de verdade:** apontar `TRACKING_BASE_URL` para o ambiente do squad e remover `TRACKING_MOCK`.

**Configuração pela interface:** a equipe cadastra a URL e a chave de API de cada squad na aba **Integrações** do menu da conta (bolinha do usuário), com botão **Testar conexão**; qualquer usuário logado vê o modo de cada integração (conectada, simulada, não configurada), sem URL nem chave. O servidor guarda a chave **cifrada** (`SETTINGS_ENCRYPTION_KEY`), exige URL `https` pública (bloqueia endereços internos) e nunca devolve a chave ao navegador. Usam a configuração: Tracking (rastreamento) e, no detalhe do pedido, **WMS** (`GET /separacao/pedidos/{id}`) e **Financeiro** (`GET /cobrancas/pedidos/{id}`). Esses dois caminhos e campos são uma PROPOSTA nossa (`contracts/consumed/{wms,financeiro}/openapi.yaml`, NÃO VERIFICADO com os squads); a tradução fica só em `src/infrastructure/clients/squads.py`. Sem URL configurada o portal mostra dados SIMULADOS, sempre rotulados; com URL e API fora do ar, mostra "indisponível" sem derrubar a tela. Frota e RH não têm integração prevista.

**Hoje:** só existe `contracts/consumed/tracking/openapi.yaml`, **uma proposta nossa (não oficial)**. Os demais squads ainda não entregaram nada (**NÃO VERIFICADO**: confirmar com eles).

## 4. Mensagem pronta para enviar aos outros squads
> Pessoal, sou do Squad 06 (CRM/SAC/Portal). Nosso contrato está em `contracts/provided/` do nosso repositório (REST em `openapi.yaml`; eventos em `contracts/provided/events/`, exchange `siglog.events`). Vocês consomem `PedidoCriado` (WMS e Financeiro) e `SinistroRegistrado` (Financeiro). Pedimos que cada squad envie o **seu** contrato (OpenAPI e/ou AsyncAPI, mais um exemplo real) por PR em `contracts/consumed/<squad>/`, ou nos mande os arquivos. Precisamos até **[data]** para o ensaio de integração. Dúvidas: [contato]. Também precisamos combinar o **RabbitMQ compartilhado** (quem hospeda) e a **autenticação entre serviços**.

## 5. Decisões a combinar entre os squads (e recomendação)
| # | Decisão | Recomendação |
|---|---|---|
| 1 | **Broker comum** | um RabbitMQ gratuito compartilhado (ex.: CloudAMQP plano free) criado por um squad; **uma credencial por squad**, repassada por canal seguro (nunca no repositório nem no chat) |
| 2 | Nomes de routing key | `<squad>.<agregado>.<evento>` em minúsculas (já usamos `customer.pedido.criado`) |
| 3 | **Auth entre serviços (REST)** | para a entrega, integrar por **eventos** (sem REST entre backends). Se for preciso REST: usuário de integração no Supabase com um perfil só de leitura (**ainda não implementado**; decidir antes de construir) |
| 4 | Correlação | `correlation_id` obrigatório, propagado nos eventos derivados e nos logs de todos os squads |
| 5 | Versionamento | campo `version`; só adicionar campos opcionais sem subir versão |
| 6 | Quem hospeda o ambiente de integração (Encontro 15) | um ambiente com broker comum + URLs públicas de cada squad |

## 6. Como as 6 soluções se juntam (Encontro 15)
- **Repositório:** o professor reúne os squads por **pastas** (nosso caso: `squad06-customer/` via fork + PR, ver `docs/19_entrega_professor.md`). Isso entrega o **código**; o **sistema no ar** depende do broker comum e das URLs de cada squad.
- **Local:** cada squad mantém o próprio `docker-compose.yml`; para integrar, todos usam o **mesmo RabbitMQ** (variável `RABBITMQ_URL`) e as URLs/mocks dos contratos. Um `docker-compose` de plataforma na raiz do repositório do professor pode incluir cada squad (opcional, depende de ele querer).

## 7. Status
| Item | Situação |
|---|---|
| Contratos que entregamos (schemas, exemplos, AsyncAPI, OpenAPI) + testes | CONFIRMADO (CI) |
| Consumidor de exemplo `scripts/consumir_eventos.py` | sintaxe conferida; **NÃO VERIFICADO** contra um RabbitMQ real |
| Mock do Tracking (`docker-compose.integracao.yml`) | configuração válida; **NÃO VERIFICADO** em execução (precisa de Docker) |
| Contratos dos squads 01, 02, 04, 05 | **PENDENTE** (nada recebido) |
| Contrato oficial do squad 03 | **PENDENTE** (usamos uma proposta nossa) |
| Broker compartilhado, auth entre serviços, ambiente de integração | **PENDENTE** de decisão entre os squads |
