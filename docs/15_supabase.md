# Supabase — banco hospedado e login

**Decisão:** o banco do Demoday é o **PostgreSQL do Supabase** (ADR-002). O Postgres em container continua para desenvolvimento e testes.
**Quem faz:** pessoa do Banco. **Segredos:** só em `.env` local ou GitHub Secrets, nunca no repositório nem em chat.

## 1. Criar o projeto
1. supabase.com → *New project* (plano Free). Guarde a senha do banco no seu gerenciador de senhas.
2. **Project Settings → Database → Connection string → Session pooler** (porta **5432**, host `...pooler.supabase.com`, usuário `postgres.<ref>`). Use o *session pooler*: ele funciona em rede só com IPv4 e aceita migrações.
3. Monte a `DATABASE_URL` no `.env` (note o prefixo `postgresql+psycopg://` e o `sslmode`):

```
DATABASE_URL=postgresql+psycopg://postgres.<ref>:<SENHA>@aws-0-<regiao>.pooler.supabase.com:5432/postgres?sslmode=require
SUPABASE_URL=https://<ref>.supabase.co
```
Senha com caracteres especiais (`@`, `/`, `#`) precisa de *URL-encode* (`@` → `%40`).

## 2. Subir a API usando o Supabase
```bash
docker compose -f docker-compose.yml -f docker-compose.supabase.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.supabase.yml logs migrate
```
O `migrate` cria as tabelas (0001) e habilita **RLS** (0002). O Postgres local não sobe neste modo.
Confira no painel: *Table Editor* mostra 8 tabelas e o ícone de RLS ativo em todas.

## 3. Por que o RLS (0002)
O Supabase expõe o schema `public` pela Data API com a chave `anon`. Com RLS ligado e **sem policies**, `anon` e `authenticated` não leem nem escrevem nada: todo acesso passa pela nossa API, que conecta com o usuário `postgres` (ignora RLS). **Não** use a chave `service_role` no front.

## 4. Login (Supabase Auth)
- **Authentication → Users → Add user** (e-mail + senha) para cada perfil de teste.
- Usuário sem papel definido entra como **cliente**. Para **atendente** ou **gestor**, no *SQL Editor*:

```sql
update auth.users
set raw_app_meta_data = coalesce(raw_app_meta_data, '{}'::jsonb) || '{"role": "atendente"}'::jsonb
where email = 'atendente@exemplo.com';
```
O papel é lido de `app_metadata` (só o servidor altera). **Nunca** de `user_metadata`, que o próprio usuário edita.
- **Validação do token:** projetos novos assinam com ES256 (JWKS, via `SUPABASE_URL`); projetos antigos usam HS256 com o *JWT Secret* (`JWT_SECRET`). A API aceita os dois.
- O front usa `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY` (a chave **anon** é pública por desenho).

## 4.1 Criar conta pelo portal (para o professor testar)
O portal tem as abas **Entrar | Criar conta**. Toda conta nova entra com o perfil **cliente** (menor privilégio) e cai no cadastro (CPF/CNPJ). Para funcionar com e-mails fictícios, ajuste uma vez no Supabase:
- **Authentication → Sign In / Providers → Email**: deixe **Allow new users to sign up** ligado e **Confirm email desligado** (senão o Supabase tenta enviar um e-mail de confirmação, que um endereço fictício nunca recebe, e o envio tem limite por hora).
- Defina o tamanho mínimo da senha (o portal exige 8 caracteres).
- Depois do Demoday, se quiser fechar as inscrições, desligue **Allow new users to sign up**.
Contas de equipe (atendente/gestor) **não** nascem pelo portal: o perfil vem de `app_metadata.role` (SQL da seção 4).

## 5. Limitações do plano Free
Projeto **pausa após cerca de 1 semana sem uso**: reative no painel antes do ensaio e do Demoday. Limite de 500 MB de dados, suficiente aqui.

## 6. Status
| Item | Situação |
|---|---|
| Código preparado (SSL, pooler, RLS, tokens do Supabase) | CONFIRMADO, 42 testes |
| Conexão real com o Supabase | **NÃO VERIFICADO** (depende do projeto criado) |
| Fluxo de login ponta a ponta | **NÃO VERIFICADO** |
