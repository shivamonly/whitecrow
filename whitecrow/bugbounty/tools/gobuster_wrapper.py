import subprocess, shutil, time, os
import urllib.request
import ssl
import concurrent.futures


COMMON_PATHS = [
    "/admin", "/login", "/wp-admin", "/administrator", "/backup",
    "/.git", "/.env", "/config", "/db", "/api", "/v1", "/v2",
    "/swagger", "/docs", "/graphql", "/robots.txt", "/sitemap.xml",
    "/crossdomain.xml", "/.htaccess", "/.htpasswd", "/wp-config.php",
    "/phpinfo.php", "/info.php", "/test.php", "/shell.php",
    "/backup.sql", "/dump.sql", "/database.sql", "/db.sql",
    "/.bash_history", "/.mysql_history", "/index.php", "/index.html",
    "/.well-known/", "/server-status", "/cgi-bin/", "/uploads",
    "/assets", "/css", "/js", "/images", "/files", "/download",
    "/private", "/internal", "/portal", "/intranet", "/dashboard",
]


def _check_path(base_url, path, timeout=4):
    url = f"{base_url.rstrip('/')}{path}"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            if r.status < 400:
                return (path, r.status, len(r.read()))
    except urllib.error.HTTPError as e:
        if e.code < 400:
            return (path, e.code, 0)
    except Exception:
        pass
    return None


def run(url, output_dir):
    start = time.time()
    results = []

    base = url.split("://")[-1].split("/")[0]

    # Try gobuster binary first
    if shutil.which("gobuster"):
        wordlist = next((w for w in [
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "/usr/share/dirb/wordlists/common.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt",
        ] if os.path.exists(w)), None)
        if wordlist:
            outfile = f"{output_dir}/gobuster_raw.txt"
            try:
                subprocess.run(
                    ["gobuster", "dir", "-u", url, "-w", wordlist, "-t", "50", "-o", outfile, "-q"],
                    capture_output=True, text=True, timeout=120
                )
                if os.path.exists(outfile):
                    with open(outfile) as f:
                        results = [l.strip() for l in f if l.strip()]
            except Exception:
                pass

    # Fallback: check common paths
    if not results:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(_check_path, url, p): p for p in COMMON_PATHS}
            for future in concurrent.futures.as_completed(futures):
                r = future.result()
                if r:
                    results.append(f"{r[0]} [{r[1]}]")

    outfile = f"{output_dir}/gobuster.txt"
    with open(outfile, "w") as f:
        f.writelines(f"{r}\n" for r in results)

    return {
        "status": "success" if results else "empty",
        "count": len(results),
        "results": results,
        "elapsed": round(time.time() - start, 2),
    }
