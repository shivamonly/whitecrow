import subprocess, shutil, time, os, socket
import urllib.request
import ssl


def _probe(url, timeout=5):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.status, dict(r.headers), len(r.read())
    except Exception:
        return None, None, None


def run(input_file, output_dir):
    start = time.time()
    results = []

    # Read domains
    domains = []
    with open(input_file) as f:
        for line in f:
            line = line.strip().lower()
            if line:
                domains.append(line)

    # Try system httpx first (faster for bulk)
    if shutil.which("httpx"):
        outfile = f"{output_dir}/httpx_raw.txt"
        try:
            subprocess.run(
                ["httpx", "-l", input_file, "-status-code", "-title", "-tech-detect", "-o", outfile, "-silent"],
                capture_output=True, text=True, timeout=120
            )
            if os.path.exists(outfile):
                with open(outfile) as f:
                    results = [l.strip() for l in f if l.strip()]
        except Exception:
            pass

    # Fallback: probe each domain with requests
    if not results:
        for domain in domains[:50]:
            for proto in ["https", "http"]:
                url = f"{proto}://{domain}"
                status, headers, size = _probe(url, timeout=4)
                if status:
                    server = headers.get("Server", "") if headers else ""
                    ct = headers.get("Content-Type", "") if headers else ""
                    results.append(f"{url} [{status}] [{server}] [{ct}]")
                    break

    outfile = f"{output_dir}/httpx.txt"
    with open(outfile, "w") as f:
        f.writelines(f"{r}\n" for r in results)

    return {
        "status": "success" if results else "empty",
        "count": len(results),
        "results": results,
        "elapsed": round(time.time() - start, 2),
    }
