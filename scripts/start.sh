#!/bin/sh
# Entrada da imagem da API. RUN_MIGRATIONS=true aplica o Alembic antes de subir (útil em hospedagem sem passo de migração).
set -e
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  alembic upgrade head
fi
exec uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
