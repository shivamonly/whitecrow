import subprocess, shutil, time, os


def run(target, output_dir):
    start = time.time()
    results = set()

    if shutil.which("amass"):
        outfile = f"{output_dir}/amass_raw.txt"
        try:
            subprocess.run(
                ["amass", "enum", "-d", target, "-o", outfile, "-passive"],
                capture_output=True, text=True, timeout=120
            )
            if os.path.exists(outfile):
                with open(outfile) as f:
                    for line in f:
                        line = line.strip().lower()
                        if line:
                            results.add(line)
        except Exception:
            pass

    return {
        "status": "success" if results else ("skipped" if not shutil.which("amass") else "empty"),
        "count": len(results),
        "results": sorted(results),
        "elapsed": round(time.time() - start, 2),
    }
