import requests
import re
import json


def investigate(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Invalid email"}
    result = {"email": email, "reputation": None, "breaches": [], "disposal": False, "domain_info": {}, "social": []}
    username, domain = email.split("@", 1)
    result["username"] = username
    result["domain"] = domain

    # reputation check
    try:
        r = requests.get(f"https://emailrep.io/{email}", headers={"User-Agent": "WhiteCrow/2.0", "Key": ""}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            result["reputation"] = {
                "reputation": d.get("reputation"),
                "suspicious": d.get("suspicious"),
                "blacklisted": d.get("details", {}).get("blacklisted"),
                "malicious_activity": d.get("details", {}).get("malicious_activity"),
                "spam": d.get("details", {}).get("spam"),
            }
    except Exception:
        pass

    # disposal / temp email detection
    try:
        r = requests.get(f"https://disposable.debounce.io/v1/{email}", headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code == 200:
            d = r.json()
            result["disposal"] = d.get("disposable") == "true"
    except Exception:
        pass

    # haveibeenpwned
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false",
                        headers={"User-Agent": "WhiteCrow", "hibp-api-key": ""}, timeout=10)
        if r.status_code == 200:
            result["breaches"] = r.json()
        elif r.status_code == 404:
            result["breaches"] = []
    except Exception:
        pass

    # domain mx / mail provider
    try:
        r = requests.get(f"https://emailrep.io/{domain}", headers={"User-Agent": "WhiteCrow/2.0"}, timeout=8)
        if r.status_code == 200:
            result["domain_info"]["mail_provider"] = r.json().get("details", {}).get("mail_provider")
    except Exception:
        pass

    # google dork for the email
    try:
        r = requests.get(f"https://www.google.com/search?q=%22{email}%22&num=10",
                        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}, timeout=8)
        if r.status_code == 200:
            links = re.findall(r'href="https?://([^"]+)"', r.text)
            result["exposure_urls"] = list(set(links))[:10]
    except Exception:
        pass

    # firebase scanner for email
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breaches?domain={domain}",
                        headers={"User-Agent": "WhiteCrow"}, timeout=8)
        if r.status_code == 200:
            domain_breaches = r.json()
            result["domain_breaches"] = [b.get("Name") for b in domain_breaches] if isinstance(domain_breaches, list) else []
    except Exception:
        pass

    return result
