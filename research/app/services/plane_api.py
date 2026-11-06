"""Plane REST calls for the offline jobs (API key, dropped connections retried by http_retry)."""
import json
import os
import sys
import urllib.error
import urllib.request

from app.services.http_retry import send


def plane(method, path, body=None, key=None):
    """JSON of the reply (None for 204). The job stops with the Plane error text on any 4xx/5xx."""
    base = os.environ.get('PLANE_URL', 'http://localhost:31080/api/v1/workspaces/ript')
    req = urllib.request.Request(
        base + path, method=method, data=json.dumps(body).encode() if body else None,
        headers={'X-API-Key': key or os.environ['PLANE_API_KEY'], 'Content-Type': 'application/json'})
    try:
        with send(req) as r:
            return json.load(r) if r.status != 204 else None
    except urllib.error.HTTPError as e:
        sys.exit(f'{method} {path} -> {e.code} {e.read()[:300]}')
