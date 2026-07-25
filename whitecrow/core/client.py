import urllib.request
import urllib.error
import ssl
import socket
import random
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urlencode

THREADS = 20
TIMEOUT = 10
PROXY_LIST = []
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]


def _ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch(url, headers=None, timeout=TIMEOUT, proxy=None):
    ctx = _ctx()
    hdrs = {"User-Agent": random.choice(USER_AGENTS), "Accept": "*/*", "Connection": "close"}
    if headers:
        hdrs.update(headers)
    try:
        req = urllib.request.Request(url, headers=hdrs)
        if proxy:
            ph = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
            opener = urllib.request.build_opener(ph)
        else:
            opener = urllib.request.build_opener()
        opener.addheaders = list(hdrs.items())
        r = opener.open(req, timeout=timeout)
        body = r.read().decode("utf-8", errors="replace")
        return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, dict(e.headers), body
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, OSError):
        return None, {}, ""


def fetch_with_rotation(url, headers=None, timeout=TIMEOUT):
    proxies = PROXY_LIST or [None]
    random.shuffle(proxies)
    for proxy in proxies[:3]:
        s, h, b = fetch(url, headers, timeout, proxy)
        if s and s not in (403, 429, 503):
            return s, h, b
        time.sleep(0.3)
    return fetch(url, headers, timeout)


def parallel(urls, timeout=TIMEOUT, workers=THREADS):
    results = {}
    def _get(u):
        return u, *fetch(u, timeout=timeout)
    with ThreadPoolExecutor(workers) as ex:
        for u, s, h, b in ex.map(_get, urls):
            results[u] = (s, h, b)
    return results


def post(url, data, headers=None, timeout=TIMEOUT):
    ctx = _ctx()
    hdrs = {"User-Agent": random.choice(USER_AGENTS), "Content-Type": "application/x-www-form-urlencoded"}
    if headers:
        hdrs.update(headers)
    body = urlencode(data).encode() if isinstance(data, dict) else data
    req = urllib.request.Request(url, data=body, headers=hdrs)
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        return r.status, dict(r.headers), r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            b = e.read().decode("utf-8", errors="replace")
        except Exception:
            b = ""
        return e.code, dict(e.headers), b
    except Exception:
        return None, {}, ""


def post_json(url, data, timeout=TIMEOUT):
    hdrs = {"Content-Type": "application/json", "User-Agent": random.choice(USER_AGENTS)}
    body = json.dumps(data).encode()
    return post(url, body, hdrs, timeout)
