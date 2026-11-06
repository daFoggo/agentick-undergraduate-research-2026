import urllib.error

import pytest

from app.services.http_retry import send


def opener(*results):
    calls = iter(results)

    def go(req, timeout=0):
        r = next(calls)
        if isinstance(r, Exception):
            raise r
        return r
    return go


def http(code):
    return urllib.error.HTTPError('u', code, 'x', {}, None)


def test_a_dropped_connection_is_retried_then_succeeds():
    assert send('r', pause=0, opener=opener(ConnectionResetError(), 'ok')) == 'ok'


def test_gateway_errors_are_retried_but_not_a_409_or_a_third_failure():
    assert send('r', pause=0, opener=opener(http(503), http(502), 'ok')) == 'ok'
    with pytest.raises(urllib.error.HTTPError):
        send('r', pause=0, opener=opener(http(409), 'ok'))
    with pytest.raises(ConnectionResetError):
        send('r', pause=0, opener=opener(*[ConnectionResetError()] * 3))
