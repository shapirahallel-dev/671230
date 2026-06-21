"""Instagram video views fetcher via Meta Graph API."""

import requests
from config import META_ACCESS_TOKEN

BASE_URL = "https://graph.facebook.com/v20.0"


def get_video_views(media_id: str) -> dict:
    """Return view count and metadata for a single Instagram media item."""
    url = f"{BASE_URL}/{media_id}"
    params = {
        "fields": "id,media_type,timestamp,video_views,like_count,comments_count",
        "access_token": META_ACCESS_TOKEN,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_views_for_account(ig_user_id: str, client_name: str) -> list[dict]:
    """Fetch recent media and return view records ready for Sheets."""
    url = f"{BASE_URL}/{ig_user_id}/media"
    params = {
        "fields": "id,media_type,timestamp,video_views,like_count,comments_count",
        "access_token": META_ACCESS_TOKEN,
        "limit": 50,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    media_items = resp.json().get("data", [])

    records = []
    for item in media_items:
        if item.get("media_type") not in ("VIDEO", "REEL"):
            continue
        records.append({
            "platform": "instagram",
            "client": client_name,
            "media_id": item["id"],
            "timestamp": item.get("timestamp"),
            "views": item.get("video_views", 0),
            "likes": item.get("like_count", 0),
            "comments": item.get("comments_count", 0),
        })
    return records
