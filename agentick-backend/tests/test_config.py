from app.core.config import Settings


def test_docs_enabled_in_local() -> None:
    assert Settings(environment="local", _env_file=None).docs_enabled is True


def test_docs_disabled_in_production() -> None:
    assert Settings(environment="production", _env_file=None).docs_enabled is False
