import os, subprocess, shutil, time


def run(input_file, output_dir):
    if not shutil.which("httpx"):
        return {"status": "skipped", "error": "httpx not found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/httpx.txt"
    try:
        subprocess.run(
            ["httpx", "-l", input_file, "-status-code", "-title", "-tech-detect", "-o", outfile],
            capture_output=True, text=True, timeout=180
        )
        lines = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                lines = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(lines), "results": lines, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "httpx timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
