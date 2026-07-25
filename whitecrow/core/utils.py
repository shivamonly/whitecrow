import re
from urllib.parse import urlparse


def extract_domain(target):
    target = target.strip().lower()
    if target.startswith("http"):
        return urlparse(target).netloc
    return target.split("/")[0]


def ensure_url(target):
    if not target.startswith("http"):
        return f"https://{target}"
    return target


def is_ip(target):
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target))


def extract_params(url):
    parsed = urlparse(url)
    if not parsed.query:
        return []
    from urllib.parse import parse_qs
    return list(parse_qs(parsed.query).keys())


def unique(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]
