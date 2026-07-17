import subprocess, shutil, time, os


WORDLISTS = [
    "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "/usr/share/dirb/wordlists/common.txt",
    "/usr/share/seclists/Discovery/Web-Content/common.txt",
]


def run(url, output_dir):
    if not shutil.which("gobuster"):
        return {"status": "skipped", "error": "gobuster not found", "results": []}
    wordlist = next((w for w in WORDLISTS if os.path.exists(w)), None)
    if not wordlist:
        return {"status": "skipped", "error": "no wordlist found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/gobuster.txt"
    domain = url.split("://")[-1].split("/")[0]
    try:
        subprocess.run(
            ["gobuster", "dir", "-u", url, "-w", wordlist, "-t", "50", "-o", outfile, "-q"],
            capture_output=True, text=True, timeout=180
        )
        lines = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                lines = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(lines), "results": lines, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "gobuster timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
