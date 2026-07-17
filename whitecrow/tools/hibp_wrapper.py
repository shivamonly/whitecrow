import requests


def run_hibp(email: str, api_key: str = "") -> dict:
    try:
        headers = {
            "User-Agent": "WhiteCrow/1.0",
            "hibp-api-key": api_key,
        } if api_key else {"User-Agent": "WhiteCrow/1.0"}
        resp = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers,
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            breaches = []
            for b in data:
                breaches.append({
                    "name": b.get("Name", ""),
                    "domain": b.get("Domain", ""),
                    "date": b.get("BreachDate", ""),
                    "data_classes": b.get("DataClasses", []),
                    "description": b.get("Description", "")[:200],
                })
            return {
                "status": "success",
                "email": email,
                "breach_count": len(breaches),
                "breaches": breaches,
            }
        elif resp.status_code == 404:
            return {"status": "success", "email": email, "breach_count": 0, "breaches": []}
        elif resp.status_code == 429:
            return {"status": "error", "error": "rate_limited"}
        return {"status": "error", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_hibp_pastes(email: str, api_key: str = "") -> dict:
    try:
        headers = {"User-Agent": "WhiteCrow/1.0"}
        if api_key:
            headers["hibp-api-key"] = api_key
        resp = requests.get(
            f"https://haveibeenpwned.com/api/v3/pasteaccount/{email}",
            headers=headers,
            timeout=15
        )
        if resp.status_code == 200:
            return {"status": "success", "pastes": resp.json()}
        elif resp.status_code == 404:
            return {"status": "success", "pastes": []}
        return {"status": "error", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
