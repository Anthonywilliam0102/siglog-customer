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

## Resultados (27/11/2026, validação local)
Ambiente: Docker local (API com 1 processo uvicorn, PostgreSQL em container, K6 na mesma máquina), 60 s por cenário. Medições do Claude do VS Code, registradas em `docs/validacao_local.md` (rodadas 7 e 8). Cada combinação foi executada **uma vez**.

| Cenário | Média | p95 | p99 | Throughput | Erros | Thresholds |
|---|---|---|---|---|---|---|
| **Normal (100 req/s)** | 113 ms | **285 ms** | 370 ms | 99,9 req/s | **0,00%** (6001 requisições) | passaram os três |
| Pico (500 req/s), 1 processo | – | 1,08 s (todas) | 1,51 s | 496,7 req/s oferecidos; ~47 req/s atendidos | 90,5% (todos 503 rápidos) | falharam |
| Pico (500 req/s), 4 processos | – | 1,39 s (todas) | 1,85 s | 491,2 req/s oferecidos; ~210 req/s atendidos | 57,7% (todos 503 rápidos) | falharam |
| Extremo (1000 req/s) | – | – | – | – | – | não executado |

### O que a medição mostrou
1. **Capacidade confortável: 100 req/s** (p95 285 ms, sem erros). É o que o sistema atende dentro dos critérios com 1 processo.
2. **Acima disso o sistema recusa, não trava.** Antes das correções, o pico esgotava o pool de conexões (5+10, espera de 30 s) e a API ficava sem resposta por vários minutos (até reinício manual). Correções: pool configurável com espera de 5 s e 503 + `Retry-After` (`77771e5`); limite de requisições em andamento (64) que recusa o excesso na entrada, e `/health` assíncrono (`0340860`).
3. **Depois das correções:** as 503 saem em cerca de 60 ms (antes, mediana de 36 s), o `/health` segue respondendo e a API volta ao normal **imediatamente** após a carga (antes, 105 a 120 s).
4. **Mais processos ajudam:** com `WEB_CONCURRENCY=4` a capacidade atendida passou de ~47 para ~210 req/s no mesmo hardware.

### Limitações (declare na apresentação)
- **Os thresholds do pico não foram atingidos:** o sistema degrada com elegância, mas não sustenta 500 req/s com p95 < 500 ms.
- **NÃO VERIFICADO:** o cenário normal depois do limitador (`0340860`); repetição das execuções (a variação entre rodadas foi grande no início); o ambiente publicado (Render free, 1 vCPU compartilhada, hiberna); o limite de conexões do Supabase com vários processos (cada processo tem o próprio pool); métricas do Prometheus são por processo quando `WEB_CONCURRENCY > 1`.
- K6 e API dividiram a mesma máquina, então os números refletem esse hardware, não produção.
