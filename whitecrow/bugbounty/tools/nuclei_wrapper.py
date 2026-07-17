import subprocess, shutil, time, os, re
import urllib.request
import ssl
import json


VULN_CHECKS = [
    ("directory_listing", "/", lambda b, h, s: "Index of /" in b),
    ("git_exposed", "/.git/config", lambda b, h, s: "[core]" in b),
    ("env_exposed", "/.env", lambda b, h, s: "APP_KEY" in b or "DB_PASSWORD" in b or "SECRET" in b),
    ("phpinfo", "/phpinfo.php", lambda b, h, s: "PHP Version" in b),
    ("admin_panel", "/admin", lambda b, h, s: s == 200 and "login" in b.lower()),
    ("debug_enabled", "/debug", lambda b, h, s: s == 200),
    ("db_exposed", "/backup.sql", lambda b, h, s: "DROP TABLE" in b or "CREATE TABLE" in b),
    ("sitemap", "/sitemap.xml", lambda b, h, s: "<urlset" in b),
    ("crossdomain", "/crossdomain.xml", lambda b, h, s: "<cross-domain-policy" in b),
    ("server_status", "/server-status", lambda b, h, s: "Server Status" in b),
    ("open_redirect", "/redirect?url=http://evil.com", lambda b, h, s: "Location" in str(h).lower()),
]


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


def run(target, output_dir):
    start = time.time()
    findings = []

    # Try nuclei binary first
    if shutil.which("nuclei"):
        outfile = f"{output_dir}/nuclei_raw.txt"
        try:
            subprocess.run(
                ["nuclei", "-u", target, "-severity", "critical,high,medium", "-o", outfile, "-json", "-silent"],
                capture_output=True, text=True, timeout=120
            )
            if os.path.exists(outfile):
                with open(outfile) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            findings.append(line)
        except Exception:
            pass

    # Fallback: basic HTTP vuln checks
    if not findings:
        for name, path, check in VULN_CHECKS:
            url = f"{target.rstrip('/')}{path}"
            try:
                status, headers, body = _fetch(url)
                if status and check(body, headers, status):
                    findings.append(json.dumps({
                        "name": name,
                        "url": url,
                        "status": status,
                        "severity": "medium" if status == 200 else "info",
                    }))
            except Exception:
                continue

    outfile = f"{output_dir}/nuclei.txt"
    with open(outfile, "w") as f:
        f.writelines(f"{f}\n" for f in findings)

    return {
        "status": "success" if findings else "empty",
        "count": len(findings),
        "results": findings,
        "elapsed": round(time.time() - start, 2),
    }
