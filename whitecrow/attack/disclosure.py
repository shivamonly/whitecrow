from ..core.client import fetch
from ..core.utils import ensure_url
from concurrent.futures import ThreadPoolExecutor, as_completed

PROBES = [
    ("robots.txt", "/robots.txt", lambda s, b, h: "Disallow:" in b or "Allow:" in b),
    ("sitemap.xml", "/sitemap.xml", lambda s, b, h: "<urlset" in b),
    (".git/config", "/.git/config", lambda s, b, h: "[core]" in b),
    (".env", "/.env", lambda s, b, h: any(x in b for x in ["APP_KEY","DB_","SECRET","PASSWORD"])),
    ("backup.sql", "/backup.sql", lambda s, b, h: any(x in b for x in ["INSERT INTO","CREATE TABLE"])),
    ("phpinfo", "/phpinfo.php", lambda s, b, h: "PHP Version" in b),
    (".htaccess", "/.htaccess", lambda s, b, h: any(x in b for x in ["RewriteRule","Deny from"])),
    (".htpasswd", "/.htpasswd", lambda s, b, h: ":" in b and len(b) < 200),
    ("server-status", "/server-status", lambda s, b, h: "Server Status" in b),
    ("server-info", "/server-info", lambda s, b, h: "Server Information" in b),
    ("crossdomain.xml", "/crossdomain.xml", lambda s, b, h: "<cross-domain-policy" in b),
    ("security.txt", "/.well-known/security.txt", lambda s, b, h: "Contact:" in b),
    ("openid-config", "/.well-known/openid-configuration", lambda s, b, h: "issuer" in b),
    ("wp-config.php", "/wp-config.php", lambda s, b, h: "DB_PASSWORD" in b or "DB_NAME" in b),
    ("package.json", "/package.json", lambda s, b, h: '"dependencies"' in b),
    ("Dockerfile", "/Dockerfile", lambda s, b, h: "FROM " in b),
    ("docker-compose", "/docker-compose.yml", lambda s, b, h: "services:" in b),
    ("terraform.tfstate", "/terraform.tfstate", lambda s, b, h: '"backend"' in b),
    ("actuator", "/actuator", lambda s, b, h: s == 200),
    ("actuator/health", "/actuator/health", lambda s, b, h: '"status"' in b),
    ("actuator/env", "/actuator/env", lambda s, b, h: '"propertySources"' in b),
]

CRITICAL = [".git/config", ".env", "wp-config.php", "backup.sql", "actuator/env"]


def check(target):
    base = ensure_url(target).rstrip("/")
    findings = []
    def _check(name, path, validator):
        u = f"{base}{path}"
        s, h, b = fetch(u)
        if s and validator(s, b, h):
            sev = "CRITICAL" if name in CRITICAL else "HIGH"
            findings.append({"name": f"Disclosure: {name}", "severity": sev, "url": u, "status": s})
    with ThreadPoolExecutor(max_workers=15) as ex:
        for n, p, v in PROBES:
            ex.submit(_check, n, p, v)
    return findings
