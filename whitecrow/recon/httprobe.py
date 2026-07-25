from ..core.client import fetch
from concurrent.futures import ThreadPoolExecutor, as_completed


def probe(hostnames):
    live = []
    def _probe(h):
        for proto in ["https", "http"]:
            s, _, _ = fetch(f"{proto}://{h}", timeout=5)
            if s and s < 500:
                return f"{proto}://{h}"
        return None
    with ThreadPoolExecutor(max_workers=30) as ex:
        for r in ex.map(_probe, hostnames):
            if r:
                live.append(r)
    return live
