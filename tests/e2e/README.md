# Teste ponta a ponta (navegador)

Percorre o portal como cliente e como atendente: cadastro (se necessário), cotação, pedido, rastreamento, chamado com SLA, sinistro,
resposta e resolução pela equipe, status até *Entregue*, avaliação da entrega e do atendimento, mais os bloqueios de perfil.

```bash
cd tests/e2e && npm install
# API (porta 8000) e front (npm run dev, porta 5173) no ar. Com o Supabase:
set -a; . ../../.env.validacao; set +a
E2E_MODE=supabase E2E_CHANNEL=chrome npm test      # E2E_CHANNEL=chrome usa o Chrome instalado (sem baixar navegador)
```
Sem Chrome: `npx playwright install chromium` e rode sem `E2E_CHANNEL`. Prints das telas: `E2E_SHOTS=./prints`.
Cria dados fictícios no banco usado pela API. O resultado sai com código 0 (tudo OK) ou 1.
