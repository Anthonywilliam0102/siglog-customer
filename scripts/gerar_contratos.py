"""Gera `contracts/provided/` (JSON Schemas, exemplos e AsyncAPI dos eventos) e `openapi.yaml` a partir do código.
Uso: python scripts/gerar_contratos.py        (rode depois de mudar rotas, schemas ou eventos; o CI confere se está atualizado)
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.domain import event_contracts as ec  # noqa: E402
from src.domain.events import ROUTING_KEYS  # noqa: E402

SAIDA = RAIZ / "contracts" / "provided"


def arquivos() -> dict[Path, str]:
    saida = {}
    for tipo in ROUTING_KEYS:
        esquema = json.dumps(ec.envelope_schema(tipo), indent=2, ensure_ascii=False)
        exemplo = json.dumps(ec.exemplo(tipo), indent=2, ensure_ascii=False)
        saida[SAIDA / "events" / f"{tipo}.schema.json"] = esquema + "\n"
        saida[SAIDA / "events" / "examples" / f"{tipo}.json"] = exemplo + "\n"
    saida[SAIDA / "asyncapi.yaml"] = yaml.safe_dump(ec.asyncapi(), allow_unicode=True, sort_keys=False)
    return saida


if __name__ == "__main__":
    for caminho, texto in arquivos().items():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "export_openapi.py")], cwd=RAIZ, check=True)
    print(f"contratos gerados em {SAIDA.relative_to(RAIZ)} e openapi.yaml")
