import requests
import re


def investigate(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Invalid email"}
    result = {"email": email, "reputation": None, "breaches": []}
    try:
        r = requests.get(f"https://emailrep.io/{email}", headers={"User-Agent": "WhiteCrow/2.0"}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            result["reputation"] = {"reputation": d.get("reputation"), "suspicious": d.get("suspicious")}
    except Exception:
        pass
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false",
                        headers={"User-Agent": "WhiteCrow"}, timeout=10)
        if r.status_code == 200:
            result["breaches"] = r.json()
    except Exception:
        pass
    return result
