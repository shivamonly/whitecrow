import re
from ..core.client import fetch
from ..core.utils import ensure_url

SIGNATURES = [
    ("Cloudflare", ["__cfduid", "cf-ray", "cloudflare-nginx", "server: cloudflare"]),
    ("Akamai", ["akamai", "akamaiedge", "edgekey", "AkamaiGHost"]),
    ("AWS WAF", ["awswaf", "x-amzn-RequestId", "x-amzn-ErrorType"]),
    ("CloudFront", ["cloudfront", "x-amz-cf-id"]),
    ("Fastly", ["fastly", "x-served-by:.*fastly"]),
    ("ModSecurity", ["mod_security", "NOYB", "Mod_Security"]),
    ("F5 BIG-IP", ["BigIP", "BIGipServer", "F5"]),
    ("Imperva", ["incapsula", "_incap_", "Imperva"]),
    ("Sucuri", ["sucuri", "cloudproxy"]),
    ("Barracuda", ["barracuda"]),
    ("Fortinet", ["fortinet", "FortiWeb", "FortiGate"]),
    ("Citrix", ["citrix", "NetScaler", "nsc_"]),
    ("Varnish", ["varnish", "X-Varnish"]),
    ("StackPath", ["stackpath"]),
    ("Comodo", ["comodo"]),
]


def detect_waf(target):
    url = ensure_url(target)
    detected = []
    try:
        s, h, b = fetch(url)
        if not s:
            return {"waf": "Unknown"}
        combined = (b + str(h) + target).lower()
        for name, patterns in SIGNATURES:
            for p in patterns:
                if re.search(p, combined, re.IGNORECASE):
                    detected.append(name)
                    break
        if not detected:
            s2, _, _ = fetch(url + "?id=1' OR '1'='1")
            if s2 and s2 != s:
                detected.append("Generic WAF (behavioral)")
    except Exception:
        pass
    return {"waf": detected[0] if detected else "None", "all": detected}
