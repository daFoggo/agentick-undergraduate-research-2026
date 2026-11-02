"""Contract tests: verify the running app's behavior matches its own OpenAPI schema."""
import schemathesis

from app.main import app

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@schema.parametrize()
def test_api_matches_schema(case):
    case.call_and_validate()
