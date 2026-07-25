import json
import urllib.request
import ssl

def _req(url, timeout=10):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        return {}


def ip_info(ip):
    result = {"ip": ip}
    try:
        data = _parse_json(_req(f"http://ip-api.com/json/{ip}?fields=66846719"))
        if data:
            result.update({
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
                "timezone": data.get("timezone"),
                "mobile": data.get("mobile"),
                "proxy": data.get("proxy"),
                "hosting": data.get("hosting"),
            })
    except Exception:
        pass
    return result


def asn_lookup(ip):
    result = {"ip": ip, "asn": None, "org": None, "cidr": None}
    try:
        data = _parse_json(_req(f"https://ipinfo.io/{ip}/json"))
        if data:
            result["org"] = data.get("org")
            result["asn"] = data.get("asn", {}).get("asn") if isinstance(data.get("asn"), dict) else data.get("asn")
            result["cidr"] = data.get("cidr")
    except Exception:
        pass
    try:
        data = _parse_json(_req(f"https://api.hackertarget.com/aslookup/?q={ip}"))
        if isinstance(data, str):
            result["raw"] = data.strip()
    except Exception:
        pass
    return result


def reverse_ip(ip):
    domains = []
    try:
        data = _parse_json(_req(f"https://api.hackertarget.com/reverseiplookup/?q={ip}"))
        if isinstance(data, str):
            for line in data.strip().split("\n"):
                line = line.strip()
                if line and " " not in line:
                    domains.append(line)
    except Exception:
        pass
    try:
        data = _parse_json(_req(f"https://yougetsignal.com/tools/web-sites-on-web-server/"))
        if isinstance(data, dict):
            for d in data.get("related", []):
                if isinstance(d, list) and len(d) > 0:
                    domains.append(d[0])
    except Exception:
        pass
    return list(set(domains))
