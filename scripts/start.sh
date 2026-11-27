#!/bin/sh
# Entrada da imagem da API. RUN_MIGRATIONS=true aplica o Alembic antes de subir (útil em hospedagem sem passo de migração).
set -e
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  alembic upgrade head
fi
# WEB_CONCURRENCY > 1 sobe mais processos (mais capacidade em carga); as métricas Prometheus ficam por processo, então use só em teste de carga.
exec uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}"
