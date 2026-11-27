# Entrega ao professor (fork + Pull Request)

Nosso repositório (fonte): `github.com/Anthonywilliam0102/siglog-customer`, branch `main` (PR #1 já mergeado).
O professor recebe o projeto por **fork do repositório dele + Pull Request**. Quem executa é uma pessoa do time, no Git Bash.

## O que combinar antes (perguntar ao professor, se não estiver no enunciado)
- URL do repositório dele e o **nome/padrão da pasta** de cada squad (ex.: `squad06-customer`).
- Se o PR deve ir para a `main` ou para outra branch, e se há modelo de descrição (template de PR).
- Se espera só o código ou também o deck do Demoday e os documentos.

## Passo a passo
1. **Fork:** no GitHub, abra o repositório do professor e clique em **Fork** (conta do time).
2. **Clonar o fork** (fora da pasta do nosso projeto) e atualizar o nosso:
```bash
git clone https://github.com/<sua-conta>/<repo-do-professor>.git ../repo-professor
cd ~/siglog-customer && git checkout main && git pull
```
3. **Copiar o projeto** para a subpasta do squad (só arquivos versionados; sem `.env`, `node_modules` ou `.git`):
```bash
sh scripts/exportar_para_professor.sh ../repo-professor squad06-customer origin/main
```
O script recusa pasta já existente e faz uma verificação de segredos (chave `sb_secret_` e tokens JWT).
4. **Commit e push no fork** (em uma branch):
```bash
cd ../repo-professor
git checkout -b entrega-squad06
git add squad06-customer
git commit -m "Squad 06: SIG-Log Customer (CRM, SAC e Portal do Cliente)"
git push -u origin entrega-squad06
```
5. **Abrir o Pull Request** no GitHub (do seu fork para o repositório do professor). Na descrição: link do nosso repositório original, URL do sistema no ar, como rodar (`README.md` da pasta) e o deck do Demoday.

## Cuidados
- **GitHub Actions:** workflows dentro de uma subpasta **não rodam** no repositório do professor. O CI continua rodando no nosso repositório original; cite isso no PR.
- Os comandos do `README.md` valem **dentro da pasta do squad** (`cd squad06-customer`).
- Mantenha o nosso repositório como fonte: correções depois do PR vão primeiro para ele; repita a cópia para uma nova branch do fork.
- **Segredos:** nunca versionar `.env`, `.env.validacao`, `frontend/.env.local`. A chave `publishable` do Supabase é pública; a `secret`/`service_role` jamais.
- Se o professor pedir o projeto na **raiz** do repositório dele (e não em subpasta), copie com o mesmo script e uma pasta temporária, e mova o conteúdo; assim os workflows passam a valer.

## Status
| Item | Situação |
|---|---|
| Script de exportação e verificação de segredos | CONFIRMADO (testado: não copia `.env`; detecta JWT vazado) |
| Fork, push e PR no repositório do professor | **PENDENTE** (depende da URL e das regras do professor) |
