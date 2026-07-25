import re
from urllib.parse import urlparse, urljoin
from ..core.client import fetch
from ..core.utils import ensure_url
from concurrent.futures import ThreadPoolExecutor, as_completed

PATTERNS = {
    "api_endpoints": re.compile(r'["\']((?:/api|/v1|/v2|/rest|/graphql)[^"\'\s]*)["\']'),
    "hidden_paths": re.compile(r'["\']((?:/admin|/internal|/private|/secret|/debug)[^"\'\s]*)["\']'),
    "tokens": re.compile(r'(?:api[_-]?key|token|secret|apikey|jwt)["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
    "ips": re.compile(r'(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})'),
    "s3": re.compile(r'["\'](https?://[a-zA-Z0-9._-]+\.s3\.amazonaws\.com[^"\'\s]*)["\']'),
    "aws_keys": re.compile(r'(AKIA[0-9A-Z]{16})'),
    "google_oauth": re.compile(r'[0-9]+-[0-9a-zA-Z_]+\.apps\.googleusercontent\.com'),
    "firebase": re.compile(r'["\'](https?://[a-zA-Z0-9_.-]+\.firebaseio\.com[^"\'\s]*)["\']'),
}


def extract_js_urls(base_url, html):
    srcs = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.I)
    urls = []
    parsed = urlparse(base_url)
    for src in srcs:
        if src.startswith("http"):
            urls.append(src)
        elif src.startswith("//"):
            urls.append("https:" + src)
        elif src.startswith("/"):
            urls.append(f"{parsed.scheme}://{parsed.netloc}{src}")
        else:
            urls.append(urljoin(base_url, src))
    return urls


def analyze(target):
    url = ensure_url(target)
    parsed = urlparse(url)
    findings = {}
    try:
        s, h, b = fetch(url)
        if not s:
            return findings
        js_urls = extract_js_urls(url, b)
        def _analyze(js_url):
            s2, h2, b2 = fetch(js_url, timeout=8)
            if not s2:
                return
            for name, pat in PATTERNS.items():
                matches = pat.findall(b2)
                if matches:
                    if name not in findings:
                        findings[name] = []
                    findings[name].extend(list(set(matches))[:10])
        with ThreadPoolExecutor(max_workers=10) as ex:
            for js in js_urls[:30]:
                ex.submit(_analyze, js)
        for name, pat in PATTERNS.items():
            matches = pat.findall(b)
            if matches:
                if name not in findings:
                    findings[name] = []
                findings[name].extend(list(set(matches))[:5])
    except Exception:
        pass
    return findings
