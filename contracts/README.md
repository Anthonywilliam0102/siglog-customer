# contracts/ — o que entregamos e o que recebemos dos outros squads

```
contracts/
├── provided/            ENTREGAMOS (gerado do código; não editar à mão)
│   ├── events/          JSON Schema de cada evento (+ examples/)
│   └── asyncapi.yaml    catálogo dos eventos (canais = routing keys)
│                        (a API REST está em ../openapi.yaml e no Swagger: /docs)
└── consumed/            RECEBEMOS (um squad por pasta; cada squad envia por Pull Request)
    ├── wms/  frota/  tracking/  financeiro/  rh/
    └── tracking/openapi.yaml   ← PROPOSTA nossa, a ser substituída pelo contrato oficial
```
Guia completo: [docs/20_integracao_squads.md](../docs/20_integracao_squads.md).

| Quero… | Comando |
|---|---|
| regenerar o que entregamos | `python scripts/gerar_contratos.py` |
| validar o que recebemos | `python scripts/validar_contratos.py` |
| ver os eventos chegando no RabbitMQ | `python scripts/consumir_eventos.py --fila minha-fila --chave customer.#` |
| subir o mock do Tracking | `docker compose -f docker-compose.yml -f docker-compose.integracao.yml up -d --build` |
