"""Browser sign-in for macOS without a privileged localhost listener."""
import secrets
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.services import riot_auth


class CallbackError(ValueError):
    pass


def start_login() -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    parsed = urlparse(riot_auth.get_auth_url())
    query = parse_qs(parsed.query)
    query.update(state=[state], nonce=[secrets.token_urlsafe(32)])
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True))), state


def validate_callback(url: str, state: str) -> str:
    """Reject unrelated, stale or ambiguous redirects without exposing their content."""
    url = url.strip()
    try:
        parsed = urlparse(url)
        valid_origin = (
            len(url) <= 20_000
            and parsed.scheme == "http"
            and parsed.hostname == "localhost"
            and parsed.port in (None, 80)
            and parsed.path == "/redirect"
            and not parsed.username
            and not parsed.password
            and not parsed.query
        )
        params = parse_qs(parsed.fragment)
        received_state = params.get("state", [])
        valid_state = (
            bool(state) and len(received_state) == 1
            and secrets.compare_digest(received_state[0], state)
        )
        valid_tokens = all(len(params.get(key, [])) == 1 for key in ("access_token", "id_token"))
    except (ValueError, TypeError):
        valid_origin = valid_state = valid_tokens = False
    if not (valid_origin and valid_state and valid_tokens):
        raise CallbackError(
            "Paste the complete localhost/redirect URL from the Riot sign-in you just opened. "
            "If you started another sign-in, cancel and connect again."
        )
    return url
