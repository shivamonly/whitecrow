from ..core.client import fetch
from ..core.utils import ensure_url


def check_cors(url):
    base = ensure_url(url)
    findings = []
    s, h, b = fetch(base)
    if not s:
        return findings

    acao = h.get("Access-Control-Allow-Origin", "")
    acac = h.get("Access-Control-Allow-Credentials", "")
    if acao == "*":
        findings.append({"name": "CORS Wildcard Origin", "severity": "HIGH", "url": base, "evidence": "ACAO: *"})
    elif acao and acac == "true":
        findings.append({"name": "CORS Reflect + Credentials", "severity": "HIGH", "url": base, "evidence": f"ACAO: {acao}, ACAC: true"})

    if not h.get("X-Frame-Options"):
        findings.append({"name": "Missing X-Frame-Options", "severity": "MEDIUM", "url": base, "evidence": "Clickjacking"})
    if not h.get("X-Content-Type-Options"):
        findings.append({"name": "Missing X-Content-Type-Options", "severity": "LOW", "url": base})
    if not h.get("Content-Security-Policy"):
        findings.append({"name": "Missing CSP", "severity": "LOW", "url": base})
    return findings
