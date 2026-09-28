#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "$(uname -s)" != Darwin ]]; then
  echo "VALSHOP Companion requires macOS." >&2
  exit 1
fi
if [[ -n "${PYTHON:-}" ]]; then
  python_bin="$PYTHON"
else
  python_bin=""
  for candidate in python3.13 python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 12))'; then
      python_bin="$candidate"
      break
    fi
  done
fi
if [[ -z "$python_bin" ]]; then
  echo "Install Python 3.12 or newer (recommended: brew install python@3.13), then rerun this script." >&2
  exit 1
fi
"$python_bin" -c 'import sys; sys.exit("Python 3.12 or newer is required") if sys.version_info < (3, 12) else None'
if [[ ! -x .venv/bin/python ]]; then
  "$python_bin" -m venv .venv
fi
.venv/bin/python -m pip install -e ./backend -e ./companion
printf '\nReady. Run: ./scripts/run_mac.sh\n'
