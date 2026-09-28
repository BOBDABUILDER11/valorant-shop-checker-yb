# VALSHOP

VALSHOP checks your VALORANT Daily Shop, bundles, wallet and Night Market, with wishlist, history, background checks, macOS notifications, Web Push and Discord alerts.

## Run on macOS

Requires macOS 13 or newer and Python 3.12 or newer. Python 3.13 is recommended. The companion opens a desktop window and stays in the Mac menu bar; Terminal is used to install and launch it. No Windows machine or VALORANT installation is needed.

If you use Homebrew, install Python with `brew install python@3.13`. Then:

```bash
git clone https://github.com/ybeeee123-wq/valorant-shop-checker-yb.git
cd valorant-shop-checker-yb
./scripts/setup_mac.sh
./scripts/run_mac.sh
```

1. Click **Connect Riot** and sign in on Riot's website in your browser.
2. When the browser redirects to `http://localhost/redirect#...`, a connection error is expected. Press **Command-L**, then **Command-C** to copy the complete address.
3. Paste it into the companion's masked input and click **Connect**. This URL contains your session: paste it only into the companion. The companion clears its input and clears the clipboard if it still contains that exact URL.
4. Click **Pair with Website** and approve this Mac in your signed-in VALSHOP account. Open the website to view the synced store and manage your wishlist, history and notification channels.
5. Close the window to keep checking from the menu bar. Use **Quit VALSHOP Companion** in that menu to stop it. Keep Terminal open while its process runs.

Under **Settings**, enable **Start VALSHOP Companion at login** for independent background operation beginning at your next login. macOS may ask you to allow background items. Keep this checkout and its `.venv` in place; disable and re-enable launch at login after moving them. **Test macOS notification** checks local delivery; allow notifications in macOS System Settings if prompted, and check Focus settings if alerts are hidden.

Later launches only need `./scripts/run_mac.sh`. To update a clean checkout, quit the companion, run `git pull`, then rerun `./scripts/setup_mac.sh` and launch again. The update button requires a configured metadata URL; see [releasing](docs/RELEASING.md).

The included configuration connects to the existing deployed website and API. To override it, copy `companion/.env.example` to `companion/.env` and set your server addresses there. Node.js is only needed to develop the website locally.

## Features and privacy

The companion retains scheduled rotation checks, capped retry backoff, wake catch-up, local shop cache/history, durable cloud upload retries, wishlist notification deduplication, revocable device pairing, launch at login, minimized launch, logs, update checks, and local Riot disconnection. Shop views, wishlist editing, history, Web Push and Discord preferences remain on the website.

Riot sessions and device credentials are stored in **macOS Keychain**. The companion sends normalized shop data to VALSHOP Cloud; it does not upload its Riot session. Login is on Riot's own website. This uses unofficial APIs; sessions expire and require local reconnection, as in the previous Windows companion. Background checks require the Mac to be awake and the companion running; overdue checks resume after wake.

Non-sensitive data is under `~/Library/Application Support/VALSHOP`; logs are under `~/Library/Logs/VALSHOP`. Startup registration is `~/Library/LaunchAgents/com.valshop.companion.plist`. Disable startup in Settings before deleting the checkout.

## Development

```bash
./scripts/setup_mac.sh
.venv/bin/python -m pip install -e 'backend[dev]' -e 'companion[dev]'
npm ci
npm --prefix frontend ci
npm run dev
```

For a local companion/server setup, copy `companion/.env.example` to `companion/.env`. Launch the companion separately with `./scripts/run_mac.sh`. Backend configuration is in `backend/.env.example` and the frontend uses `VITE_API_URL`.

Checks:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest backend/tests companion/tests -q
.venv/bin/python -m ruff check backend/app backend/tests companion
.venv/bin/python -m mypy backend/app
npm --prefix frontend run lint
npm --prefix frontend run build
```

`companion/` contains the Python/PySide6 macOS app, `backend/` the FastAPI service and shared Riot parsing, and `frontend/` the React/Vite website. This repository now targets a Mac companion launched from source; the previous Windows installer workflow has been retired.

See [architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY.md), [releasing](docs/RELEASING.md) and [deployment](DEPLOYMENT.md). VALSHOP is independent and is not affiliated with or endorsed by Riot Games.
