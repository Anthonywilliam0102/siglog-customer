"""Gera um JWT de DESENVOLVIMENTO para testar a API localmente (expira em 8 h por padrão).

Uso: JWT_SECRET=... python scripts/gen_token.py <sub> <cliente|atendente|gestor> [horas]
"""
import os
import sys
import time

import jwt

sub, role = sys.argv[1], sys.argv[2]
horas = float(sys.argv[3]) if len(sys.argv) > 3 else 8
secret = os.environ["JWT_SECRET"]
print(jwt.encode({"sub": sub, "role": role, "exp": int(time.time() + horas * 3600)}, secret, algorithm="HS256"))
