from ..core.client import fetch
from ..core.utils import ensure_url
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINTS = [
    "/api", "/api/v1", "/api/v2", "/api/v3", "/rest", "/api/rest",
    "/api/health", "/api/status", "/api/version", "/api/ping",
    "/swagger.json", "/swagger/v1/swagger.json", "/api/swagger.json",
    "/openapi.json", "/api/openapi.json", "/api/docs",
    "/api/users", "/api/user", "/api/admin", "/api/config",
    "/api/graphql", "/graphql",
    "/.well-known/openid-configuration",
]


def check_api(url):
    base = ensure_url(url).rstrip("/")
    findings = []
    def _check(path):
        u = f"{base}{path}"
        s, h, b = fetch(u)
        if s and s < 500:
            return {"name": f"API: {path}", "severity": "INFO", "url": u, "status": s}
        return None
    with ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(_check, ENDPOINTS):
            if r:
                findings.append(r)
    return findings
