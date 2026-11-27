# Context Map

```
                +------------------+
  Cliente ----> |  CRM/Customer    | (este squad)  — porta de entrada
                +--------+---------+
                         | PedidoCriado (evento)
          +--------------+---------------+
          v                              v
        WMS                          FINANCEIRO  <--- SinistroRegistrado
   (separação)                  (frete, cobrança,
                                 estorno/indenização)
                         ^
   Tracking --(REST: GET rastreamento / eventos de status)--+
   Frota -> Tracking -> (via propagação do fluxo)
```

| Relação | Contextos | Padrão | Mecanismo |
|---|---|---|---|
| Customer → WMS | publica `PedidoCriado` | Published Language / Pub-Sub | RabbitMQ |
| Customer → Financeiro | publica `PedidoCriado`, `SinistroRegistrado` | Published Language / Pub-Sub | RabbitMQ |
| Customer ← Tracking | consulta rastreamento / consome status | Customer-Supplier + ACL | REST (OpenAPI do Tracking) |
| Customer ↔ RH | sem integração direta prevista | — | — |

**Anti-Corruption Layer:** o Customer traduz o modelo do Tracking para a visão do cliente (ex.: códigos de status técnicos → texto amigável) em `src/infrastructure/clients/`.

> **PENDENTE:** confirmar nomes de filas/exchanges e contratos com os demais squads e o Context Map geral.
