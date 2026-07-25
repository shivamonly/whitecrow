import requests
import re


def investigate(phone):
    cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone)
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    result = {"phone": phone, "e164": cleaned, "messaging": {}}
    try:
        r = requests.get(f"https://wa.me/{cleaned.replace('+','')}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8, allow_redirects=False)
        result["messaging"]["whatsapp"] = r.status_code in (200, 301, 302)
    except Exception:
        result["messaging"]["whatsapp"] = None
    try:
        r = requests.get(f"https://t.me/{cleaned.replace('+','')}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        result["messaging"]["telegram"] = r.status_code == 200
    except Exception:
        result["messaging"]["telegram"] = None
    return result
