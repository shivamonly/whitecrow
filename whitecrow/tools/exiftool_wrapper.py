import subprocess
import json
import shutil


EXIFTOOL_AVAILABLE = shutil.which("exiftool") is not None


def run_exiftool(photo_path: str, timeout: int = 15) -> dict:
    if not EXIFTOOL_AVAILABLE:
        return {"status": "skipped", "error": "exiftool not found on system PATH"}
    try:
        result = subprocess.run(
            ["exiftool", "-json", photo_path],
            capture_output=True, text=True, timeout=timeout
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            if data:
                return {"status": "success", "metadata": data[0]}
        return {"status": "success", "metadata": {}}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
