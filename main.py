"""Data fetcher — pulls from APIs and returns records for the dashboard."""

import logging
from clients import CLIENTS
from instagram import fetch_views_for_account as ig_fetch
from tiktok import fetch_views_for_account as tt_fetch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def fetch_all() -> list[dict]:
    """Fetch view data for all clients across all platforms."""
    records = []
    for client in CLIENTS:
        name = client["name"]
        log.info("Fetching: %s", name)

        if ig_id := client.get("instagram_user_id"):
            try:
                records.extend(ig_fetch(ig_id, name))
            except Exception as e:
                log.error("Instagram error [%s]: %s", name, e)

        if tt_id := client.get("tiktok_open_id"):
            try:
                records.extend(tt_fetch(tt_id, name))
            except Exception as e:
                log.error("TikTok error [%s]: %s", name, e)

    return records


if __name__ == "__main__":
    data = fetch_all()
    log.info("Fetched %d records total.", len(data))
