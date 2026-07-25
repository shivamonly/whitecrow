from ..core.client import fetch
from concurrent.futures import ThreadPoolExecutor, as_completed

PATHS = [
    "/admin", "/login", "/backup", "/config", "/api", "/swagger",
    "/wp-admin", "/wp-content", "/wp-includes", "/wp-login.php",
    "/.git/config", "/.git/HEAD", "/.env", "/.svn", "/.DS_Store",
    "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
    "/phpmyadmin", "/pma", "/administrator",
    "/server-status", "/server-info",
    "/uploads", "/files", "/download", "/backup",
    "/test", "/dev", "/staging", "/beta",
    "/.well-known/security.txt", "/.well-known/openid-configuration",
    "/api/health", "/api/status", "/api/version",
    "/graphql", "/api/graphql",
    "/package.json", "/Dockerfile", "/docker-compose.yml",
    "/README.md", "/config.json", "/database.yml",
    "/.htaccess", "/.htpasswd",
    "/phpinfo.php", "/info.php", "/test.php",
    "/backup.sql", "/database.sql", "/dump.sql",
    "/error", "/error.log", "/debug",
    "/actuator", "/actuator/health", "/actuator/info",
    "/api-docs", "/swagger.json", "/openapi.json",
    "/terraform.tfstate",
]


def discover(url):
    base = url.rstrip("/")
    found = []
    def _check(path):
        u = f"{base}{path}"
        try:
            s, h, b = fetch(u, timeout=5)
            if s and s not in (404, 400):
                return {"url": u, "status": s, "size": len(b), "type": h.get("Content-Type", "")}
        except Exception:
            pass
        return None
    with ThreadPoolExecutor(max_workers=20) as ex:
        for r in ex.map(_check, PATHS):
            if r:
                found.append(r)
    return found
