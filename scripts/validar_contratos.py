"""Valida os contratos RECEBIDOS dos outros squads (`contracts/consumed/**`). Roda no CI.
Regras mínimas: o arquivo precisa ser YAML/JSON válido e, se for OpenAPI/AsyncAPI, ter versão e conteúdo (paths/channels).
Uso: python scripts/validar_contratos.py
"""
import json
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "contracts" / "consumed"


def validar(arquivo: Path) -> list[str]:
    try:
        texto = arquivo.read_text(encoding="utf-8")
        doc = json.loads(texto) if arquivo.suffix == ".json" else yaml.safe_load(texto)
    except Exception as exc:  # noqa: BLE001 - qualquer erro de leitura/sintaxe é falha do contrato
        return [f"não é um {arquivo.suffix[1:].upper()} válido: {exc}"]
    erros = []
    if isinstance(doc, dict) and "openapi" in doc:
        if not str(doc["openapi"]).startswith("3."):
            erros.append("`openapi` deve ser 3.x")
        if not doc.get("info", {}).get("title"):
            erros.append("falta `info.title`")
        if not doc.get("paths"):
            erros.append("`paths` vazio")
    if isinstance(doc, dict) and "asyncapi" in doc and not doc.get("channels"):
        erros.append("`channels` vazio")
    return erros


def main() -> int:
    arquivos = sorted(p for p in PASTA.rglob("*") if p.suffix in {".yaml", ".yml", ".json"})
    falhas = 0
    for a in arquivos:
        erros = validar(a)
        print(("FALHA " if erros else "OK    ") + str(a.relative_to(RAIZ)) + ("" if not erros else " -> " + "; ".join(erros)))
        falhas += bool(erros)
    tem_contrato = lambda d: any(p.suffix in {".yaml", ".yml", ".json"} for p in d.rglob("*"))  # noqa: E731
    pendentes = [d.name for d in sorted(PASTA.iterdir()) if d.is_dir() and not tem_contrato(d)]
    if pendentes:
        print("Aguardando contrato de:", ", ".join(pendentes))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
