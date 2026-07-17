import subprocess, shutil, time


def run(target, output_dir):
    if not shutil.which("wafw00f"):
        return {"status": "skipped", "error": "wafw00f not found", "results": []}
    start = time.time()
    try:
        r = subprocess.run(["wafw00f", target], capture_output=True, text=True, timeout=60)
        return {"status": "success", "result": r.stdout.strip(), "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "wafw00f timed out", "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "elapsed": round(time.time() - start, 2)}
