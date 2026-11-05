from app.core.security import valid_bearer


def test_empty_secret_never_validates():
    assert not valid_bearer("Bearer anything", "")


def test_missing_or_malformed_header_never_validates():
    assert not valid_bearer(None, "secret")
    assert not valid_bearer("secret", "secret")


def test_matching_bearer_validates():
    assert valid_bearer("Bearer secret", "secret")
