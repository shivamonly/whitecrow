import requests


def check_whatsapp(phone: str, timeout: int = 10) -> dict:
    try:
        clean = phone.lstrip("+").replace(" ", "")
        resp = requests.get(
            f"https://wa.me/{clean}",
            allow_redirects=True, timeout=timeout
        )
        exists = "send?phone" not in resp.url
        return {"status": "success", "whatsapp_registered": exists, "url": f"https://wa.me/{clean}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_telegram(phone: str, timeout: int = 10) -> dict:
    try:
        resp = requests.post(
            "https://my.telegram.org/auth/send_password",
            data={"phone": phone},
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=timeout
        )
        if resp.status_code == 200:
            return {"status": "success", "telegram_registered": True}
        return {"status": "success", "telegram_registered": False}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_signal(phone: str, timeout: int = 10) -> dict:
    try:
        clean = phone.lstrip("+").replace(" ", "")
        resp = requests.get(
            f"https://signal.tube/#{clean}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=timeout
        )
        return {"status": "success", "signal_available": True, "note": "Signal is available for all numbers"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
