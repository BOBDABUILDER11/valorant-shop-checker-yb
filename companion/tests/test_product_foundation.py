import json
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pytest

import preferences
from callback import CallbackError, start_login, validate_callback
from credentials import CredentialStore
from local_riot import LocalRiotClient
from local_store import LocalStore


class MemoryCredentials:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, name: str) -> str | None:
        return self.values.get((service, name))

    def set_password(self, service: str, name: str, value: str) -> None:
        self.values[(service, name)] = value

    def delete_password(self, service: str, name: str) -> None:
        self.values.pop((service, name), None)


def test_credentials_and_riot_session_restore() -> None:
    backend = MemoryCredentials()
    credentials = CredentialStore(backend)
    session = {
        "access_token": "sensitive" * 500,
        "puuid": "player",
        "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }
    credentials.save_riot_session(session)
    credentials.save_device_token("device-secret")
    assert LocalRiotClient(credentials).session == session
    assert json.loads(backend.values[("VALSHOP", "riot_session")])["format"] == "chunked-v1"
    assert len([name for service, name in backend.values if name.startswith("riot_session.")]) > 1
    assert credentials.device_token() == "device-secret"
    credentials.clear_riot_session()
    credentials.clear_device_token()
    assert credentials.riot_session() is None
    assert credentials.device_token() == ""


def test_legacy_single_value_riot_session_is_still_readable() -> None:
    backend = MemoryCredentials()
    backend.set_password("VALSHOP", "riot_session", json.dumps({"puuid": "legacy"}))
    credentials = CredentialStore(backend)
    assert credentials.riot_session() == {"puuid": "legacy"}
    credentials.clear_riot_session()
    assert credentials.riot_session() is None


def test_offline_queue_history_and_notification_dedupe(tmp_path) -> None:
    store = LocalStore(str(tmp_path / "cache.db"))
    shop = {
        "rotation_key": "rotation-1",
        "fetched_at": datetime.now(UTC).isoformat(),
        "seconds_remaining": 300,
        "offers": [{"uuid": "skin", "name": "Skin", "cost": 875}],
    }
    store.save_shop(shop)
    assert store.get_cache("shop")["rotation_key"] == "rotation-1"
    assert store.pending() == [shop]
    assert len(store.history()) == 1
    assert store.should_notify("rotation-1", "skin") is True
    assert store.should_notify("rotation-1", "skin") is False
    store.mark_uploaded("rotation-1")
    assert store.pending() == []


def test_preferences_persist(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "settings.json"
    monkeypatch.setattr(preferences, "SETTINGS_FILE", path)
    first = preferences.Preferences()
    first.set("launch_minimized", True)
    assert preferences.Preferences().get("launch_minimized") is True


def test_login_state_is_unique_and_validates_redirect() -> None:
    auth_url, state = start_login()
    params = parse_qs(urlparse(auth_url).query)
    assert params["state"] == [state]
    assert params["nonce"] != ["1"]
    assert start_login()[1] != state
    callback = f"http://localhost/redirect#access_token=test&id_token=test-id&state={state}"
    assert validate_callback(callback, state) == callback


@pytest.mark.parametrize("url", [
    "http://evil.example/redirect#access_token=test&id_token=id&state=expected",
    "http://localhost:8080/redirect#access_token=test&id_token=id&state=expected",
    "http://localhost/redirect#access_token=test&id_token=id&state=other",
    "http://localhost/redirect#access_token=test&id_token=id",
    "http://localhost/redirect#access_token=test&access_token=other&id_token=id&state=expected",
    "http://localhost/redirect#access_token=test&id_token=id&state=expected&state=other",
    "http://user@localhost/redirect#access_token=test&id_token=id&state=expected",
    "http://localhost:bad/redirect#access_token=test&id_token=id&state=expected",
    "http://localhost/redirect?access_token=test#id_token=id&state=expected",
])
def test_invalid_login_does_not_expose_tokens(url: str) -> None:
    with pytest.raises(CallbackError) as error:
        validate_callback(url, "expected")
    assert "access_token" not in str(error.value)
    assert url not in str(error.value)
