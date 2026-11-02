"""Dump the app's OpenAPI schema to a file without starting a server."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

if __name__ == "__main__":
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    out_path.write_text(json.dumps(app.openapi(), indent=2))
    print(f"wrote {out_path}")
