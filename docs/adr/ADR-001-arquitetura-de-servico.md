# ADR-001 — Arquitetura do serviço
**Status:** Aceita

**Contexto:** Módulo do SIG-Log que deve seguir DDD, camadas e Database-per-Service (Project Kit §4).
**Problema:** Que estilo de serviço usar sem sobre-engenharia para um projeto acadêmico de 4 pessoas?
**Alternativas:** (a) monólito modular em camadas; (b) microsserviço em camadas com Outbox; (c) vários microsserviços por agregado.
**Decisão:** (b) um microsserviço FastAPI em camadas (API → Application → Domain → Infrastructure).
**Justificativa:** atende ao enunciado, é simples de operar em Docker e ensina DDD. (c) seria custo excessivo.
**Consequências:** `Session` do SQLAlchemy atua como Unit of Work diretamente nos casos de uso (pragmático; os repositórios não foram abstraídos). Regras puras ficam em `domain/`. Trade-off: acoplamento da camada de aplicação ao ORM em troca de menos código.
