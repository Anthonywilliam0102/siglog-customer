"""Exporta o contrato para openapi.yaml (rode após alterar rotas/schemas)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.api.main import app  # noqa: E402

try:
    import yaml
except ImportError:  # fallback: JSON é YAML válido
    yaml = None

spec = app.openapi()
out = Path("openapi.yaml")
if yaml:
    text = yaml.safe_dump(spec, allow_unicode=True, sort_keys=False)
else:
    text = json.dumps(spec, indent=2, ensure_ascii=False)
out.write_text(text)
print(f"gerado {out}")
