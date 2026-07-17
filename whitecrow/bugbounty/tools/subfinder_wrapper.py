import subprocess
import shutil
import time


def run(target, output_dir):
    if not shutil.which("subfinder"):
        return {"status": "skipped", "error": "subfinder not found", "results": []}
    start = time.time()
    outfile = f"{output_dir}/subfinder.txt"
    try:
        subprocess.run(
            ["subfinder", "-d", target, "-all", "-o", outfile],
            capture_output=True, text=True, timeout=120
        )
        with open(outfile) as f:
            subs = [l.strip() for l in f if l.strip()]
        return {"status": "success", "count": len(subs), "results": subs, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "subfinder timed out", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
