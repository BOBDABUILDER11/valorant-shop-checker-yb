import plistlib
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QInputDialog
from test_product_foundation import MemoryCredentials

import desktop
import startup
from credentials import CredentialStore
from local_store import LocalStore


def test_login_registration_uses_arguments_and_can_be_removed(tmp_path, monkeypatch):
    path = tmp_path / "folder with spaces" / "companion.plist"
    monkeypatch.setattr(startup, "AGENT_FILE", path)
    monkeypatch.setattr(startup, "LOG_DIR", tmp_path)
    monkeypatch.setattr(startup, "ensure_directories", lambda: None)
    monkeypatch.setattr(startup.sys, "platform", "darwin")
    monkeypatch.setattr(startup.sys, "executable", "/path with spaces/.venv/bin/python")
    startup.set_startup(True)
    payload = plistlib.loads(path.read_bytes())
    assert payload["ProgramArguments"][0] == "/path with spaces/.venv/bin/python"
    assert Path(payload["ProgramArguments"][1]).name == "launcher.py"
    assert payload["ProgramArguments"][2] == "--minimized"
    assert payload["RunAtLoad"] and not payload["KeepAlive"]
    assert path.stat().st_mode & 0o777 == 0o600
    assert startup.startup_enabled()
    startup.set_startup(False)
    startup.set_startup(False)
    assert not startup.startup_enabled()


@pytest.fixture
def window(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    values = {"launch_minimized": False, "close_notice_shown": True}
    class Preferences:
        def get(self, key):
            return values.get(key)
        def set(self, key, value):
            values[key] = value
    monkeypatch.setattr(desktop, "Preferences", Preferences)
    monkeypatch.setattr(desktop, "CredentialStore", lambda: CredentialStore(MemoryCredentials()))
    monkeypatch.setattr(desktop, "LocalStore", lambda: LocalStore(str(tmp_path / "cache.db")))
    monkeypatch.setattr(desktop, "configure_logging", lambda: None)
    monkeypatch.setattr(desktop.MainWindow, "_startup", lambda self: None)
    widget = desktop.MainWindow()
    yield widget
    widget.quit_app()
    widget.close()
    app.processEvents()


def test_cancel_login_preserves_session_and_restores_controls(window, monkeypatch):
    session = {"puuid": "existing"}
    window.riot.session = session
    monkeypatch.setattr(desktop.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(QInputDialog, "exec", lambda self: QDialog.DialogCode.Rejected)
    window.connect_riot()
    assert window.riot.session is session
    assert window.connect_button.isEnabled()
    assert window.tray_reconnect.isEnabled()
    assert window.connect_button.text() == "Reconnect Riot"


def test_browser_failure_does_not_leave_login_disabled(window, monkeypatch):
    monkeypatch.setattr(desktop.webbrowser, "open", lambda url: False)
    errors = []
    monkeypatch.setattr(window, "show_error", errors.append)
    window.connect_riot()
    assert errors and "browser" in errors[0]
    assert window.connect_button.isEnabled()


def test_valid_login_clears_clipboard_and_schedules_local_connection(window, monkeypatch):
    url = "http://localhost/redirect#access_token=test&id_token=id&state=expected"
    monkeypatch.setattr(desktop, "start_login", lambda: ("https://auth.riotgames.com", "expected"))
    monkeypatch.setattr(desktop.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(QInputDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    monkeypatch.setattr(QInputDialog, "textValue", lambda self: url)
    tasks = []
    monkeypatch.setattr(window, "run_worker", lambda *args, **kwargs: tasks.append((args, kwargs)))
    QApplication.clipboard().setText(url)
    window.connect_riot()
    assert QApplication.clipboard().text() == ""
    assert len(tasks) == 1
    tasks[0][1]["on_finished"]()
    assert window.connect_button.isEnabled()
