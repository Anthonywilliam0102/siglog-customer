// Teste de carga K6 — SIG-Log Customer.
// Uso: k6 run -e BASE_URL=http://localhost:8000 -e TOKEN=<jwt cliente> -e CUSTOMER_ID=<uuid> -e SCENARIO=normal tests/load/k6.js
// SCENARIO: normal (100 req/s) | pico (500 req/s) | extremo (1000 req/s)
import http from 'k6/http';
import { check } from 'k6';

const RATES = { normal: 100, pico: 500, extremo: 1000 };
const rate = RATES[__ENV.SCENARIO || 'normal'];

export const options = {
  scenarios: {
    carga: {
      executor: 'constant-arrival-rate',
      rate, timeUnit: '1s', duration: '60s',
      preAllocatedVUs: Math.min(rate, 200), maxVUs: rate * 2,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
  },
  summaryTrendStats: ['avg', 'p(95)', 'p(99)', 'max'],
};

const headers = { Authorization: `Bearer ${__ENV.TOKEN}`, 'Content-Type': 'application/json' };
const BASE = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // 80% leituras leves, 20% escrita (cotação) — proporção típica de portal
  if (Math.random() < 0.8) {
    const r = http.get(`${BASE}/customers/${__ENV.CUSTOMER_ID}`, { headers });
    check(r, { 'GET customer 200': (x) => x.status === 200 });
  } else {
    const r = http.post(`${BASE}/quotes`, JSON.stringify({
      customer_id: __ENV.CUSTOMER_ID, origem: 'São Paulo/SP', destino: 'Recife/PE', peso_kg: 50, volume_m3: 0.5,
    }), { headers });
    check(r, { 'POST quote 201': (x) => x.status === 201 });
  }
}
