import requests
import json
import socket
from ..core.client import fetch


def investigate(ip):
    result = {"ip": ip, "hostname": None, "rdns": None, "geo": {}, "asn": {}, "threat": {}, "services": [], "domains": []}

    try:
        result["hostname"] = socket.gethostbyaddr(ip)[0]
    except Exception:
        pass

    try:
        result["rdns"] = socket.getnameinfo((ip, 0), socket.NI_NAMEREQD)[0]
    except Exception:
        pass

    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code == 200:
            d = r.json()
            result["geo"] = {
                "country": d.get("country"),
                "region": d.get("regionName"),
                "city": d.get("city"),
                "zip": d.get("zip"),
                "lat": d.get("lat"),
                "lon": d.get("lon"),
                "isp": d.get("isp"),
                "org": d.get("org"),
                "as": d.get("as"),
                "timezone": d.get("timezone"),
            }
            result["threat"] = {
                "proxy": d.get("proxy"),
                "hosting": d.get("hosting"),
                "mobile": d.get("mobile"),
            }
    except Exception:
        pass

    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code == 200:
            d = r.json()
            result["asn"]["asn"] = d.get("org", "").split(" ", 1)[0] if d.get("org") else None
            result["asn"]["org"] = d.get("org")
            result["asn"]["cidr"] = d.get("city")
    except Exception:
        pass

    try:
        r = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90",
                        headers={"User-Agent": "Mozilla/5.0", "Key": ""}, timeout=8)
        if r.status_code == 200:
            d = r.json().get("data", {})
            result["threat"]["abuse_score"] = d.get("abuseConfidenceScore")
            result["threat"]["reports"] = d.get("totalReports")
    except Exception:
        pass

    try:
        r = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            for line in r.text.strip().split("\n"):
                line = line.strip()
                if line and " " not in line and "." in line:
                    result["domains"].append(line)
    except Exception:
        pass

    # shodan-like service banner grab on common ports
    common_web = [80, 443, 8080, 8443, 8000, 8888]
    banners = []
    for port in common_web:
        try:
            s, h, b = fetch(f"http://{ip}:{port}", timeout=3) if port != 443 else fetch(f"https://{ip}:{port}", timeout=3)
            if s:
                server = h.get("Server", "")
                title = ""
                if "<title>" in b:
                    title = b.split("<title>")[1].split("</title>")[0][:60]
                banners.append({"port": port, "status": s, "server": server, "title": title})
        except Exception:
            pass
    result["banners"] = banners

    return result
