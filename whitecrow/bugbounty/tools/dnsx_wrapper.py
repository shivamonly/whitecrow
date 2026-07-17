import subprocess, shutil, time, os


def run(input_file, output_dir):
    if not shutil.which("dnsx"):
        return {"status": "skipped", "error": "dnsx not found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/dnsx.txt"
    try:
        subprocess.run(
            ["dnsx", "-l", input_file, "-a", "-cname", "-resp", "-o", outfile],
            capture_output=True, text=True, timeout=120
        )
        lines = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                lines = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(lines), "results": lines, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "dnsx timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
