# Releasing VALSHOP for macOS

The companion is distributed as source and launched from Terminal. `companion/version.py` is the desktop version. Tag that version as `vX.Y.Z` after the macOS workflow passes. There is no Windows installer or macOS binary signing step for this source distribution.

Production endpoint defaults live in `companion/release_config.json`. `companion/.env` can override `API_BASE_URL`, `PUBLIC_SITE_URL`, `UPDATE_METADATA_URL`, and `UPDATE_DOWNLOAD_URL`. Configure an HTTPS metadata endpoint returning `{"version":"1.2.3","download_url":"https://github.com/ybeeee123-wq/valorant-shop-checker-yb#run-on-macos"}` to enable the in-app update check. The update button opens instructions; quit the companion, pull changes in a clean checkout, rerun setup and restart.

Before releasing, run the checks in the root README on macOS. Manually verify sign-in with a real Riot account, shop/wallet/bundle/Night Market sync, pairing and revocation, notifications with permissions enabled, menu bar actions, startup after logout/login and wake catch-up. Automated checks use synthetic sessions and do not establish that live Riot authentication or cloud deployment is functioning.

Deploy the backend and frontend following `DEPLOYMENT.md`, configure companion endpoints, and publish the source tag and metadata together. Web Push and Discord remain backend notification channels.
