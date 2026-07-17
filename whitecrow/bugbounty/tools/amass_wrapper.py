import subprocess, shutil, time, os


def run(target, output_dir):
    if not shutil.which("amass"):
        return {"status": "skipped", "error": "amass not found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/amass.txt"
    try:
        subprocess.run(
            ["amass", "enum", "-d", target, "-o", outfile, "-passive"],
            capture_output=True, text=True, timeout=180
        )
        subs = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                subs = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(subs), "results": subs, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "amass timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
