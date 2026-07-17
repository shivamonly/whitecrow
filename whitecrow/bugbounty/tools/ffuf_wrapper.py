from .gobuster_wrapper import run


def run(url, output_dir):
    # Reuse the same logic — ffuf binary fallback if available
    import subprocess, shutil, time, os
    base = url.split("://")[-1].split("/")[0]
    start = time.time()
    results = []

    if shutil.which("ffuf"):
        wordlist = next((w for w in [
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "/usr/share/dirb/wordlists/common.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt",
        ] if os.path.exists(w)), None)
        if wordlist:
            outfile = f"{output_dir}/ffuf_raw.txt"
            try:
                subprocess.run(
                    ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist, "-t", "100", "-o", outfile, "-of", "csv", "-ac", "-s"],
                    capture_output=True, text=True, timeout=120
                )
                if os.path.exists(outfile):
                    with open(outfile) as f:
                        results = [l.strip() for l in f if l.strip()]
            except Exception:
                pass

    if not results:
        from .gobuster_wrapper import COMMON_PATHS, _check_path
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(_check_path, url, p): p for p in COMMON_PATHS}
            for future in concurrent.futures.as_completed(futures):
                r = future.result()
                if r:
                    results.append(f"{r[0]} [{r[1]}]")

    return {
        "status": "success" if results else "empty",
        "count": len(results),
        "results": results,
        "elapsed": round(time.time() - start, 2),
    }
