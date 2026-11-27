#!/bin/sh
# Copia o projeto (somente arquivos versionados) para uma subpasta de um clone/fork do repositório do professor.
# Uso (na raiz do nosso repositório, depois de `git pull`):
#   sh scripts/exportar_para_professor.sh <pasta-do-fork> <subpasta-do-squad> [ref]
# Exemplo: sh scripts/exportar_para_professor.sh ../repo-professor squad06-customer origin/main
# Nunca copia .env, .env.validacao, node_modules nem a pasta .git (git archive só leva o que está no Git).
set -eu
FORK="${1:?Informe a pasta do clone/fork do repositório do professor}"
DEST="${2:?Informe o nome da subpasta do squad (ex.: squad06-customer)}"
REF="${3:-origin/main}"

[ -d "$FORK/.git" ] || { echo "ERRO: '$FORK' não é um repositório Git."; exit 1; }
git rev-parse --verify "$REF" >/dev/null 2>&1 || { echo "ERRO: referência '$REF' não existe. Rode 'git fetch' ou informe outra (ex.: HEAD)."; exit 1; }
TARGET="$FORK/$DEST"
if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "ERRO: '$TARGET' já existe e não está vazia. Escolha outro nome ou remova a pasta."; exit 1
fi

mkdir -p "$TARGET"
git archive "$REF" | tar -x -C "$TARGET"
N=$(find "$TARGET" -type f | wc -l | tr -d ' ')
echo "OK: $N arquivos de '$REF' copiados para '$TARGET'."
# Padrões de segredo reais: chave secreta do Supabase e tokens JWT. (Senhas de exemplo como siglog_dev não contam.)
PADRAO="sb_secret_[A-Za-z0-9_]{10,}|eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\."
if grep -rIlE "$PADRAO" "$TARGET" >/dev/null 2>&1; then
  echo "ATENÇÃO: possível segredo encontrado nos arquivos copiados. Revise antes de commitar:"
  grep -rIlE "$PADRAO" "$TARGET" || true
  exit 2
fi
echo "Verificação de segredos: limpo."
echo "Próximos passos no fork:  cd \"$FORK\" && git checkout -b entrega-squad06 && git add \"$DEST\" && git commit -m \"Squad 06: SIG-Log Customer\" && git push -u origin entrega-squad06"
