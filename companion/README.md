# VALSHOP macOS Companion

From the repository root, run `./scripts/setup_mac.sh`, then `./scripts/run_mac.sh`. See the [complete Mac setup guide](../README.md#run-on-macos) for Python requirements, Riot sign-in, website pairing, notifications, startup, updating and troubleshooting.

The PySide6 window and menu bar app reuse the shared Riot/store parsing and cloud sync. Riot sessions and device credentials use macOS Keychain. Closing the window keeps the process running; quitting it stops background checks.

Riot redirects to port 80, which is privileged on macOS. The companion opens your browser and accepts the full redirect URL in a masked dialog. It validates the redirect origin and per-login state locally; it never starts a privileged server. Cancel leaves the existing connection untouched. Reconnect locally when Riot's session expires.

Settings registers optional startup for the next login through `~/Library/LaunchAgents/com.valshop.companion.plist`. It uses this checkout's Python interpreter and launcher, runs without a shell or administrator rights, and honors explicit Quit. Disabling startup removes registration for subsequent logins and leaves the current session running.

`companion/.env` is read consistently whether launched from Terminal or at login. Its values override `release_config.json`. For local services, copy `.env.example` to `.env`. Production defaults are already included in `release_config.json`.
