import json
import ssl
import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def _req(url, timeout=15):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _crt_sh(domain):
    try:
        data = json.loads(_req(f"https://crt.sh/?q=%25.{domain}&output=json"))
        subs = set()
        for e in data:
            for n in e.get("name_value", "").split("\n"):
                n = n.strip().lower()
                if n and (n.endswith("." + domain) or n == domain):
                    subs.add(n)
        return subs
    except Exception:
        return set()


def _alienvault(domain):
    try:
        data = json.loads(_req(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"))
        return {e.get("hostname", "").strip().lower() for e in data.get("passive_dns", []) if e.get("hostname")}
    except Exception:
        return set()


def _urlscan(domain):
    try:
        data = json.loads(_req(f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=100"))
        return {r.get("page", {}).get("domain", "").strip().lower() for r in data.get("results", []) if r.get("page", {}).get("domain")}
    except Exception:
        return set()


def _hackertarget(domain):
    try:
        text = _req(f"https://api.hackertarget.com/hostsearch/?q={domain}")
        subs = set()
        for line in text.strip().split("\n"):
            if "," in line:
                subs.add(line.split(",")[0].strip().lower())
        return subs
    except Exception:
        return set()


def _rapiddns(domain):
    try:
        html = _req(f"https://rapiddns.io/subdomain/{domain}?full=1")
        subs = set()
        for m in re.finditer(r'<td>([^<]+)</td>', html):
            v = m.group(1).strip().lower()
            if v.endswith("." + domain):
                subs.add(v)
        return subs
    except Exception:
        return set()


def _bufferover(domain):
    try:
        data = json.loads(_req(f"https://dns.bufferover.run/dns?q=.{domain}"))
        subs = set()
        for e in data.get("FDNS_A", []):
            parts = e.split(",")
            if len(parts) >= 2:
                subs.add(parts[1].strip().lower())
        return subs
    except Exception:
        return set()


def _certspotter(domain):
    try:
        data = json.loads(_req(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"))
        subs = set()
        for e in data:
            for n in e.get("dns_names", []):
                n = n.strip().lower()
                if n.endswith("." + domain):
                    subs.add(n)
        return subs
    except Exception:
        return set()


SOURCES = [
    ("crt.sh", _crt_sh),
    ("AlienVault", _alienvault),
    ("urlscan.io", _urlscan),
    ("HackerTarget", _hackertarget),
    ("RapidDNS", _rapiddns),
    ("BufferOver", _bufferover),
    ("CertSpotter", _certspotter),
]


def enum(domain):
    domain = domain.strip().lower()
    if domain.startswith("http"):
        from urllib.parse import urlparse
        domain = urlparse(domain).netloc

    all_subs = set()
    all_subs.add(domain)

    with ThreadPoolExecutor(max_workers=7) as ex:
        futures = {ex.submit(func, domain): name for name, func in SOURCES}
        for f in as_completed(futures):
            try:
                all_subs.update(f.result())
            except Exception:
                pass

    all_subs.discard("")
    all_subs.discard(domain)
    all_subs.discard("*." + domain)
    return sorted(all_subs)
