import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "config", ".env"))

META_ACCESS_TOKEN    = os.getenv("META_ACCESS_TOKEN", "")
TIKTOK_ACCESS_TOKEN  = os.getenv("TIKTOK_ACCESS_TOKEN", "")
