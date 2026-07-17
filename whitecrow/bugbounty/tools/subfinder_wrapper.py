import subprocess, shutil, time, json
import urllib.request
import ssl


def _crt_sh(domain):
    try:
        ctx = ssl.create_default_context()
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
            data = json.loads(r.read().decode())
        subs = set()
        for entry in data:
            name = entry.get("name_value", "")
            for n in name.split("\n"):
                n = n.strip().lower()
                if n.endswith(f".{domain}") or n == domain:
                    subs.add(n)
        return subs
    except Exception:
        return set()


def _alienvault(domain):
    try:
        ctx = ssl.create_default_context()
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read().decode())
        subs = set()
        for entry in data.get("passive_dns", []):
            host = entry.get("hostname", "").strip().lower()
            if host:
                subs.add(host)
        return subs
    except Exception:
        return set()


def _urlscan(domain):
    try:
        ctx = ssl.create_default_context()
        url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            data = json.loads(r.read().decode())
        subs = set()
        for result in data.get("results", []):
            page = result.get("page", {})
            host = page.get("domain", "").strip().lower()
            if host:
                subs.add(host)
        return subs
    except Exception:
        return set()


def run(target, output_dir):
    start = time.time()
    all_subs = set()
    results = {}

    # API-based enumeration (no binary needed)
    apis = [
        ("crt.sh", _crt_sh),
        ("AlienVault OTX", _alienvault),
        ("urlscan.io", _urlscan),
    ]
    for name, func in apis:
        try:
            subs = func(target)
            results[name] = len(subs)
            all_subs.update(subs)
        except Exception:
            results[name] = 0

    # System binary fallback
    if shutil.which("subfinder"):
        outfile = f"{output_dir}/subfinder_raw.txt"
        try:
            subprocess.run(
                ["subfinder", "-d", target, "-all", "-o", outfile, "-silent"],
                capture_output=True, text=True, timeout=60
            )
            with open(outfile) as f:
                for line in f:
                    line = line.strip().lower()
                    if line:
                        all_subs.add(line)
            results["subfinder_bin"] = "used"
        except Exception:
            results["subfinder_bin"] = "failed"

    if shutil.which("amass"):
        outfile = f"{output_dir}/amass_raw.txt"
        try:
            subprocess.run(
                ["amass", "enum", "-d", target, "-o", outfile, "-passive"],
                capture_output=True, text=True, timeout=120
            )
            with open(outfile) as f:
                for line in f:
                    line = line.strip().lower()
                    if line:
                        all_subs.add(line)
            results["amass_bin"] = "used"
        except Exception:
            results["amass_bin"] = "failed"

    # save
    outfile = f"{output_dir}/subfinder.txt"
    with open(outfile, "w") as f:
        f.writelines(f"{s}\n" for s in sorted(all_subs))

    return {
        "status": "success" if all_subs else "empty",
        "count": len(all_subs),
        "api_sources": results,
        "results": sorted(all_subs),
        "elapsed": round(time.time() - start, 2),
    }
