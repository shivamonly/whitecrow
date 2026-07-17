import subprocess
import json
import shutil
import tempfile
from pathlib import Path


MAIGRET_AVAILABLE = shutil.which("maigret") is not None


def run_maigret(username: str, timeout: int = 60) -> dict:
    if not MAIGRET_AVAILABLE:
        return {"status": "skipped", "error": "maigret not installed (pip install maigret)"}
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = Path(tmpdir) / "maigret_output.json"
            result = subprocess.run(
                ["maigret", username, "--json", str(outfile),
                 "--timeout", "10", "--no-recursion", "--no-extracting"],
                capture_output=True, text=True, timeout=timeout
            )
            profiles = []
            if outfile.exists():
                with open(outfile) as f:
                    data = json.load(f)
                for site, info in data.get("sites", {}).items():
                    if isinstance(info, dict) and info.get("status") == 1:
                        profiles.append({
                            "site": site,
                            "url": info.get("url", ""),
                            "name": info.get("username", username),
                        })
            return {
                "status": "success",
                "username": username,
                "profiles_found": len(profiles),
                "profiles": profiles,
                "raw_output": result.stdout[:2000]
            }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
