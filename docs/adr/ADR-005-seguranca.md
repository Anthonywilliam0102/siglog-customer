# ADR-005 — Estratégia de segurança
**Status:** Aceita

**Decisão:** JWT Bearer com perfis (cliente/atendente/gestor), autorização por dono do recurso (RN02), segredos em variáveis de ambiente/GitHub Secrets, scan Trivy no CI e SonarCloud.
**Alternativas:** sessão própria; OAuth2 completo com IdP; Supabase Auth.
**Justificativa:** validar JWT é simples e compatível com Supabase Auth (gratuito) sem acoplar o domínio ao provedor.
**Consequências:** HS256 com segredo compartilhado é aceitável para o projeto acadêmico; produção exigiria RS256/JWKS, rate limiting e rotação de segredos. Ver docs/11_security.md.
