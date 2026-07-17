import subprocess, shutil, time, os


def run(target, output_dir):
    if not shutil.which("nuclei"):
        return {"status": "skipped", "error": "nuclei not found. Install: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "results": []}
    start = time.time()
    outfile = f"{output_dir}/nuclei.txt"
    try:
        subprocess.run(
            ["nuclei", "-u", target, "-severity", "critical,high,medium", "-o", outfile, "-json", "-silent"],
            capture_output=True, text=True, timeout=300
        )
        findings = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        findings.append(line)
        return {"status": "success", "count": len(findings), "results": findings, "elapsed": round(time.time() - start, 2)}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "nuclei timed out (5 min)", "results": [], "elapsed": round(time.time() - start, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e), "results": [], "elapsed": round(time.time() - start, 2)}
