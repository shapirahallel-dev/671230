"""TikTok video views fetcher via TikTok Research API."""

import requests
from config import TIKTOK_ACCESS_TOKEN

BASE_URL = "https://open.tiktokapis.com/v2"


def fetch_views_for_account(open_id: str, client_name: str) -> list[dict]:
    """Fetch recent videos and return view records ready for Sheets."""
    url = f"{BASE_URL}/video/list/"
    headers = {"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
    payload = {
        "fields": ["id", "create_time", "view_count", "like_count", "comment_count"],
        "filters": {"video_ids": []},  # empty = fetch latest
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    videos = resp.json().get("data", {}).get("videos", [])

    records = []
    for v in videos:
        records.append({
            "platform": "tiktok",
            "client": client_name,
            "media_id": v.get("id"),
            "timestamp": v.get("create_time"),
            "views": v.get("view_count", 0),
            "likes": v.get("like_count", 0),
            "comments": v.get("comment_count", 0),
        })
    return records
