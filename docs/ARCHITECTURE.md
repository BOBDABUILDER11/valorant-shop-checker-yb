# VALSHOP architecture

## Trust boundaries

The macOS companion owns Riot authentication. It opens Riot in the user's browser, then accepts the complete localhost redirect URL in a masked dialog. A random per-login state binds that URL to the initiated sign-in. It uses no privileged listener. Tokens are exchanged locally and the resulting session is stored in macOS Keychain. The companion does not send its Riot credentials to the VALSHOP cloud.

The companion fetches storefront, wallet, bundle, and Night Market data directly from Riot and parses it with the shared backend service modules. It writes the last known normalized view, wishlist cache, history, notification keys, and pending uploads to a local SQLite database. A reset-aware Qt timer schedules one fetch after the storefront reset with jitter; failures use capped exponential backoff. Work runs through `QThreadPool`, never the UI thread.

Cloud pairing uses a public random challenge plus a private verifier. The browser sees only the challenge. The server stores hashes, binds approval to the signed-in website user, encrypts the one-time credential until it is polled, and stores only the permanent device credential hash afterward. Each Mac has an independent revocable credential.

The FastAPI service stores normalized snapshots, wishlist, devices, preferences, delivery subscriptions, and notification dedupe records. SQLite supports development; the same SQLAlchemy models run against Postgres/Supabase in production. The React website calls FastAPI over HTTPS and preserves the existing shop experience.

## Data flow

1. Desktop authenticates locally with Riot and fetches a rotation.
2. Desktop commits the normalized rotation and notification dedupe key locally.
3. If paired, desktop uploads pending normalized snapshots using its device bearer token.
4. Backend validates and deduplicates the rotation, evaluates wishlist matches, and dispatches enabled cloud channels.
5. If cloud is unavailable, the desktop remains usable and retries its durable pending queue later.

Logs rotate under `~/Library/Logs/VALSHOP`; sensitive-field filters prevent tokens, authorization values, and webhook material from being logged.
