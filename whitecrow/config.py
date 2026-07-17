import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

EMAILREP_API_KEY = os.getenv("EMAILREP_API_KEY", "")
HIBP_API_KEY = os.getenv("HIBP_API_KEY", "")
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "30"))
