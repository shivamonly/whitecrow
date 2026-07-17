import subprocess
import re
import shutil


SHERLOCK_AVAILABLE = shutil.which("python3") is not None


def _sherlock_importable() -> bool:
    try:
        import sherlock_project
        return True
    except ImportError:
        return False


SHERLOCK_LINE_RE = re.compile(r"^\[\+\]\s+(.+?):\s+(https?://\S+)")


def run_sherlock(username: str, timeout: int = 60) -> dict:
    if not _sherlock_importable():
        return {"status": "skipped", "error": "sherlock-project not installed (pip install sherlock-project)"}
    try:
        result = subprocess.run(
            [sys_executable(), "-m", "sherlock_project", username,
             "--timeout", "10", "--no-color"],
            capture_output=True, text=True, timeout=timeout
        )
        profiles = []
        for line in result.stdout.splitlines():
            m = SHERLOCK_LINE_RE.match(line)
            if m:
                profiles.append({
                    "site": m.group(1),
                    "url": m.group(2).rstrip("/"),
                    "username": username,
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


def sys_executable() -> str:
    import sys
    return sys.executable
