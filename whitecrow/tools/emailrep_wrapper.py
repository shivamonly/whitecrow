import requests


def run_emailrep(email: str, api_key: str = "") -> dict:
    try:
        headers = {"User-Agent": "WhiteCrow/1.0"}
        if api_key:
            headers["Key"] = api_key
        resp = requests.get(
            f"https://emailrep.io/{email}",
            headers=headers,
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "success",
                "email": email,
                "reputation": data.get("reputation", "unknown"),
                "suspicious": data.get("suspicious", False),
                "blacklisted": data.get("blacklisted", False),
                "details": data.get("details", {}),
                "breaches": data.get("details", {}).get("breaches", []),
            }
        return {"status": "error", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
