"""Gera um JWT de DESENVOLVIMENTO para testar a API localmente.

Uso: JWT_SECRET=... python scripts/gen_token.py <sub> <cliente|atendente|gestor>
"""
import os
import sys

import jwt

sub, role = sys.argv[1], sys.argv[2]
secret = os.environ["JWT_SECRET"]
print(jwt.encode({"sub": sub, "role": role}, secret, algorithm="HS256"))
