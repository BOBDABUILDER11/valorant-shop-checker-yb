"""Register the source companion for the next macOS login, without administrator access."""
import os
import plistlib
import sys
from pathlib import Path

from paths import LOG_DIR, ensure_directories

AGENT_FILE = Path.home() / "Library" / "LaunchAgents" / "com.valshop.companion.plist"


def startup_enabled() -> bool:
    return AGENT_FILE.is_file()


def set_startup(enabled: bool) -> None:
    if sys.platform != "darwin":
        raise RuntimeError("VALSHOP Companion requires macOS.")
    if not enabled:
        AGENT_FILE.unlink(missing_ok=True)
        return
    ensure_directories()
    launcher = Path(__file__).resolve().with_name("launcher.py")
    payload = {
        "Label": "com.valshop.companion",
        "ProgramArguments": [sys.executable, str(launcher), "--minimized"],
        "WorkingDirectory": str(launcher.parent.parent),
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Interactive",
        "LimitLoadToSessionType": "Aqua",
        "StandardOutPath": str(LOG_DIR / "launch-agent.log"),
        "StandardErrorPath": str(LOG_DIR / "launch-agent-error.log"),
    }
    AGENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = AGENT_FILE.with_suffix(".tmp")
    try:
        temporary.write_bytes(plistlib.dumps(payload))
        temporary.chmod(0o600)
        os.replace(temporary, AGENT_FILE)
    finally:
        temporary.unlink(missing_ok=True)
