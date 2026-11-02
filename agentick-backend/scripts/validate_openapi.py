"""Validate the app's generated OpenAPI schema against the OpenAPI JSON Schema."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openapi_spec_validator import validate  # noqa: E402

from app.main import app  # noqa: E402

if __name__ == "__main__":
    schema = app.openapi()
    validate(schema)
    print(f"OpenAPI {schema['openapi']} schema is valid.")
