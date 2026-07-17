import subprocess
import shutil


HOLEHE_AVAILABLE = shutil.which("holehe") is not None


def run_holehe(email: str, timeout: int = 60) -> dict:
    if not HOLEHE_AVAILABLE:
        return {"status": "skipped", "error": "holehe not installed (pip install holehe)"}
    try:
        result = subprocess.run(
            ["holehe", email, "--no-color", "--only-used", "-T", "15"],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        sites_found = []
        for line in output.splitlines():
            if "[" not in line or "%|" in line:
                continue
            if "]" in line and "✓" in line:
                parts = line.split("]", 1)
                if len(parts) > 1:
                    site = parts[1].strip()
                    if site and "not" not in site.lower():
                        sites_found.append(site)
        return {
            "status": "success",
            "email": email,
            "registrations": sites_found,
            "raw_output": output[:2000]
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr[:500] if e.stderr else str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
