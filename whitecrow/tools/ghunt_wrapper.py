import subprocess
import re
import shutil


GHUNT_AVAILABLE = shutil.which("ghunt") is not None


def run_ghunt(email: str, timeout: int = 60) -> dict:
    if not GHUNT_AVAILABLE:
        return {"status": "skipped", "error": "ghunt not installed (pip install ghunt)"}
    try:
        result = subprocess.run(
            ["ghunt", "email", email],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        info = {}
        lines = output.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if ":" in line and not line.startswith("[") and not line.startswith("|"):
                key = line.split(":", 1)[0].strip().lower().replace(" ", "_")
                val = line.split(":", 1)[1].strip()
                if val and val != "None":
                    info[key] = val
            if "google account id" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    info["google_id"] = parts[1].strip()
            if "gaia id" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    info["gaia_id"] = parts[1].strip()
            match = re.search(r'https?://\S+', line)
            if match and "avatar" in line.lower():
                info["avatar_url"] = match.group(0)
            if "name" in line.lower() and ":" in line and i < 15:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    if name and len(name) < 50:
                        info["display_name"] = name
            if "youtube" in line.lower() and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    info["youtube_channel"] = parts[1].strip()
            for key in ("calendar", "review", "maps"):
                if key in line.lower() and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        val = parts[1].strip()
                        if val and val != "None":
                            info[f"google_{key}"] = val

        return {
            "status": "success" if info else "no_data",
            "email": email,
            "profile": info,
            "raw_output": output[:3000]
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout"}
    except FileNotFoundError:
        return {"status": "error", "error": "ghunt not installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
