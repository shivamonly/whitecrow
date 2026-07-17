import urllib.request, ssl, json, time, re
from concurrent.futures import ThreadPoolExecutor, as_completed


def _fetch(url, timeout=5):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", errors="ignore")
    except Exception:
        return None, {}, ""


INFO_DISCLOSURE_CHECKS = [
    ("robots.txt", "/robots.txt", lambda b, h, s: "Disallow:" in b or "Allow:" in b),
    ("sitemap.xml", "/sitemap.xml", lambda b, h, s: "<urlset" in b or "<sitemap" in b),
    ("git_config", "/.git/config", lambda b, h, s: "[core]" in b),
    ("env_file", "/.env", lambda b, h, s: "APP_KEY" in b or "DB_" in b or "SECRET" in b or "PASSWORD" in b),
    ("backup_sql", "/backup.sql", lambda b, h, s: "INSERT INTO" in b or "CREATE TABLE" in b),
    ("phpinfo", "/phpinfo.php", lambda b, h, s: "PHP Version" in b),
    ("ds_store", "/.DS_Store", lambda b, h, s: b"00" in b.encode() if b else False),
    ("htaccess", "/.htaccess", lambda b, h, s: "RewriteRule" in b or "Deny from" in b),
    ("htpasswd", "/.htpasswd", lambda b, h, s: ":" in b and len(b) < 200),
    ("server_status", "/server-status", lambda b, h, s: "Server Status" in b),
    ("server_info", "/server-info", lambda b, h, s: "Server Information" in b),
    ("crossdomain", "/crossdomain.xml", lambda b, h, s: "<cross-domain-policy" in b),
    ("clientaccess", "/clientaccesspolicy.xml", lambda b, h, s: "<access-policy" in b),
    ("security_txt", "/.well-known/security.txt", lambda b, h, s: "Contact:" in b),
    ("openid_config", "/.well-known/openid-configuration", lambda b, h, s: "issuer" in b),
]

AUTH_CHECKS = [
    ("login_page", "/login", lambda b, h, s: s == 200 and ("login" in b.lower() or "password" in b.lower())),
    ("register", "/register", lambda b, h, s: s == 200),
    ("password_reset", "/forgot-password", lambda b, h, s: s == 200),
    ("admin_panel", "/admin", lambda b, h, s: s == 200 and ("admin" in b.lower() or "dashboard" in b.lower())),
    ("graphql", "/graphql", lambda b, h, s: s in (200, 405)),
    ("graphql_console", "/graphql?query={__schema{types{name}}}", lambda b, h, s: "__schema" in b),
    ("swagger", "/swagger.json", lambda b, h, s: "swagger" in b.lower() or "openapi" in b.lower()),
    ("swagger_ui", "/swagger", lambda b, h, s: "swagger" in b.lower()),
    ("api_docs", "/api/docs", lambda b, h, s: s == 200),
]

CORS_CHECKS = [
    ("cors_wildcard", lambda h: h.get("Access-Control-Allow-Origin") == "*"),
    ("cors_reflect", lambda h: h.get("Access-Control-Allow-Origin") == "null"),
    ("cors_credentials", lambda h: h.get("Access-Control-Allow-Credentials") == "true"),
]

SSRF_CHECKS = [
    ("cloud_metadata_aws", "http://169.254.169.254/latest/meta-data/", lambda b, h, s: s == 200),
    ("cloud_metadata_gcp", "http://metadata.google.internal/computeMetadata/v1/", lambda b, h, s: s == 200),
]


def run_info_disclosure(target, output_dir):
    base = f"https://{target}"
    findings = []
    for name, path, check in INFO_DISCLOSURE_CHECKS:
        url = f"{base}{path}"
        try:
            s, h, b = _fetch(url)
            if s and check(b, h, s):
                findings.append({"type": name, "url": url, "status": s, "severity": "high" if "git" in name or "env" in name or "sql" in name else "medium"})
        except Exception:
            continue
    return {"status": "success" if findings else "empty", "count": len(findings), "results": findings}


def run_auth_checks(target, output_dir):
    base = f"https://{target}"
    findings = []
    for name, path, check in AUTH_CHECKS:
        url = f"{base}{path}"
        try:
            s, h, b = _fetch(url)
            if s and check(b, h, s):
                findings.append({"type": name, "url": url, "status": s, "severity": "info"})
        except Exception:
            continue
    return {"status": "success" if findings else "empty", "count": len(findings), "results": findings}


def run_cors_checks(target, output_dir):
    base = f"https://{target}"
    try:
        s, h, b = _fetch(base, timeout=8)
        findings = []
        for name, check in CORS_CHECKS:
            if check(h):
                findings.append({"type": name, "url": base, "severity": "high" if "wildcard" in name else "medium"})
        return {"status": "success" if findings else "empty", "count": len(findings), "results": findings}
    except Exception:
        return {"status": "error", "results": []}


def run_ssrf_checks(target, output_dir):
    findings = []
    for name, url, check in SSRF_CHECKS:
        try:
            s, h, b = _fetch(url, timeout=3)
            if s and check(b, h, s):
                findings.append({"type": name, "url": url, "severity": "critical"})
        except Exception:
            continue
    return {"status": "success" if findings else "empty", "count": len(findings), "results": findings}


def run(target, output_dir):
    start = time.time()
    results = {}

    phases = [
        ("info_disclosure", run_info_disclosure),
        ("auth_endpoints", run_auth_checks),
        ("cors", run_cors_checks),
        ("ssrf", run_ssrf_checks),
    ]

    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(func, target, output_dir): name for name, func in phases}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}

    return {
        "status": "success",
        "results": results,
        "total_findings": sum(r.get("count", 0) for r in results.values()),
        "elapsed": round(time.time() - start, 2),
    }
