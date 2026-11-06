"""urlopen that survives a dropped connection (seen once against Plane: RemoteDisconnected)."""
import time
import urllib.error
import urllib.request


def send(req, tries=3, pause=2.0, opener=urllib.request.urlopen):
    """Retries a dropped connection, a timeout or a 502/503/504; any other HTTP error goes to the caller.
    Re-sending is safe for post_briefs: briefs are replaced on re-run and alerts are overwritten."""
    for attempt in range(tries):
        try:
            return opener(req, timeout=30)
        except urllib.error.HTTPError as e:
            if e.code not in (502, 503, 504) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(pause * (attempt + 1))
