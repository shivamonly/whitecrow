import subprocess, shutil, time, os
import socket


def _resolve(domain):
    try:
        addrs = socket.getaddrinfo(domain, 80, socket.AF_INET)
        ips = list(set(a[4][0] for a in addrs))
        return ips
    except Exception:
        return []


def run(input_file, output_dir):
    start = time.time()
    results = []

    with open(input_file) as f:
        domains = [l.strip() for l in f if l.strip()]

    # Try system dnsx first
    if shutil.which("dnsx"):
        outfile = f"{output_dir}/dnsx_raw.txt"
        try:
            subprocess.run(
                ["dnsx", "-l", input_file, "-a", "-cname", "-resp", "-o", outfile, "-silent"],
                capture_output=True, text=True, timeout=60
            )
            if os.path.exists(outfile):
                with open(outfile) as f:
                    results = [l.strip() for l in f if l.strip()]
        except Exception:
            pass

    # Fallback: Python socket resolution
    if not results:
        for domain in domains:
            ips = _resolve(domain)
            if ips:
                results.append(f"{domain} [A: {', '.join(ips)}]")
            else:
                results.append(f"{domain} [NXDOMAIN]")

    outfile = f"{output_dir}/dnsx.txt"
    with open(outfile, "w") as f:
        f.writelines(f"{r}\n" for r in results)

    return {
        "status": "success" if results else "empty",
        "count": len(results),
        "results": results,
        "elapsed": round(time.time() - start, 2),
    }
