# Validação local (executor no VS Code)

Arquivo do **Claude do VS Code**: adicionar sempre no fim, uma seção por rodada, com data, comandos e resultado
(CONFIRMADO / NÃO VERIFICADO / FALHOU). Não colar segredos. O checklist (`00_checklist.md`) é mantido pelo Claude da nuvem.

## 2026-11-23 — Rodada 1
- CONFIRMADO: build, migrate (0001), fluxo cliente → cotação → pedido, RN02 (403) e RN07 (422), Outbox publicado.
- FALHOU e corrigido (`1d2bc7d`): `httpx` fora do `requirements.txt`; API caía em loop na imagem.
- CONFIRMADO: Jaeger com traces da API; Grafana com login, datasource e dashboard; 9 de 12 painéis com dados.
- NÃO VERIFICADO: aparência do dashboard no navegador; painéis de tickets/sinistros/satisfação com dados.
