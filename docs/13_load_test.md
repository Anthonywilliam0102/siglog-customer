# Teste de Carga (K6)

Script: [`tests/load/k6.js`](../tests/load/k6.js) · Executor `constant-arrival-rate`, 60 s por cenário.

| Cenário | Taxa | Critérios (thresholds) |
|---|---|---|
| Normal | 100 req/s | falhas < 1%, p95 < 500 ms, p99 < 1 s |
| Pico | 500 req/s | idem |
| Extremo | 1000 req/s | idem (esperado degradar; registrar o ponto de ruptura) |

Mix: 80% `GET /customers/{id}`, 20% `POST /quotes`.

## Como executar
```bash
docker compose up -d --build
export JWT_SECRET=$(grep JWT_SECRET .env | cut -d= -f2)
TOKEN=$(python scripts/gen_token.py k6-user cliente)
CUSTOMER_ID=$(curl -s -X POST localhost:8000/customers -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"nome":"Cliente Carga","documento":"11222333000181","tipo":"PJ","email":"carga@exemplo.com"}' | python -c 'import sys,json;print(json.load(sys.stdin)["id"])')
for s in normal pico extremo; do
  docker run --rm -i --network host -e BASE_URL=http://localhost:8000 -e TOKEN=$TOKEN -e CUSTOMER_ID=$CUSTOMER_ID -e SCENARIO=$s \
    grafana/k6 run - < tests/load/k6.js
done
```
Acompanhe em paralelo o Grafana (http://localhost:3000, dashboard *SIG-Log Customer*) e o Jaeger.

## Resultados
> **PENDENTE DE EXECUÇÃO** — preencher após rodar (latência média, p95, p99, throughput, taxa de erros) e anexar prints do Grafana.

| Cenário | Média | p95 | p99 | Throughput | Erros |
|---|---|---|---|---|---|
| Normal | – | – | – | – | – |
| Pico | – | – | – | – | – |
| Extremo | – | – | – | – | – |

**Limitação conhecida:** a API roda com 1 processo uvicorn e o banco é um container na mesma máquina; os números refletem o hardware do laptop, não produção.
