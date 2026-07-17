import subprocess
import shutil


HARVESTER_AVAILABLE = shutil.which("theHarvester") is not None


def run_theharvester(email: str, timeout: int = 30) -> dict:
    if not HARVESTER_AVAILABLE:
        return {"status": "skipped", "error": "theHarvester not found on system PATH"}
    domain = email.split("@")[-1]
    try:
        result = subprocess.run(
            ["theHarvester", "-d", domain, "-b", "all", "-l", "50"],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        hosts = []
        ips = []
        employees = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("[+] Host"):
                hosts.append(line.replace("[+] Host:", "").strip())
            elif line.startswith("[+] IP"):
                ips.append(line.replace("[+] IP:", "").strip())
            elif line.startswith("[+] Employee"):
                employees.append(line.replace("[+] Employee:", "").strip())
        return {
            "status": "success",
            "domain": domain,
            "hosts": hosts,
            "ips": ips,
            "employees": employees,
            "raw_output": output[:2000]
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
