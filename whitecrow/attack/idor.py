from ..core.client import fetch
from ..core.utils import ensure_url

PATHS = [
    ("user_id", "/api/users/{}"),
    ("id", "/api/items/{}"),
    ("uid", "/api/profile/{}"),
    ("account_id", "/api/accounts/{}"),
    ("customer_id", "/api/customers/{}"),
    ("order_id", "/api/orders/{}"),
    ("document_id", "/api/documents/{}"),
]


def check_idor(url):
    base = ensure_url(url).rstrip("/")
    findings = []
    for param, path_tmpl in PATHS:
        for uid in [1, 2, 100, 1000, 9999]:
            u = f"{base}{path_tmpl.format(uid)}"
            s, h, b = fetch(u)
            if s and s < 400 and len(b) > 50:
                findings.append({
                    "name": f"IDOR: {param}={uid}",
                    "severity": "HIGH",
                    "url": u,
                    "status": s
                })
                break
    return findings
