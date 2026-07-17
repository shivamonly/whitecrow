import subprocess, shutil, time, os


WORDLISTS = [
    "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "/usr/share/dirb/wordlists/common.txt",
    "/usr/share/seclists/Discovery/Web-Content/common.txt",
]


def run(url, output_dir):
    if not shutil.which("ffuf"):
        return {"status": "skipped", "error": "ffuf not found", "results": []}
    wordlist = next((w for w in WORDLISTS if os.path.exists(w)), None)
    if not wordlist:
        return {"status": "skipped", "error": "no wordlist found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/ffuf.txt"
    try:
        subprocess.run(
            ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist, "-t", "100", "-o", outfile, "-of", "csv", "-ac"],
            capture_output=True, text=True, timeout=180
        )
        lines = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                lines = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(lines), "results": lines, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "ffuf timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
