import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


def resolve(hostnames):
    results = {}
    def _resolve(h):
        try:
            return h, socket.gethostbyname(h)
        except Exception:
            return h, None
    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = {ex.submit(_resolve, h): h for h in hostnames}
        for f in as_completed(futures):
            h, ip = f.result()
            if ip:
                results[h] = ip
    return results
