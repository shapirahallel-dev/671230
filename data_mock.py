"""Demo data — replace with real API calls once tokens are configured."""

import pandas as pd
import random
from datetime import datetime, timedelta

CLIENTS = ["Brand Alpha", "Studio Nova", "Luxe Co.", "Peak Ventures"]
PLATFORMS = ["instagram", "tiktok"]


def generate_mock_data() -> pd.DataFrame:
    random.seed(42)
    rows = []
    for client in CLIENTS:
        for platform in PLATFORMS:
            for i in range(12):
                date = datetime.now() - timedelta(days=i * 3)
                rows.append({
                    "client": client,
                    "platform": platform,
                    "date": date.strftime("%Y-%m-%d"),
                    "views": random.randint(10_000, 500_000),
                    "likes": random.randint(500, 20_000),
                    "comments": random.randint(50, 3_000),
                    "video_id": f"{platform[:2].upper()}-{random.randint(10000,99999)}",
                })
    return pd.DataFrame(rows)
