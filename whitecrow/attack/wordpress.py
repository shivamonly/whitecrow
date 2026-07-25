from ..core.client import fetch, post as http_post
from ..core.utils import ensure_url
from urllib.parse import urlencode
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

CHECKS = [
    ("wp-json", "/wp-json/", lambda s, b, h: s == 200),
    ("wp-json/users", "/wp-json/wp/v2/users/", lambda s, b, h: s == 200),
    ("wp-login", "/wp-login.php", lambda s, b, h: s == 200),
    ("wp-admin", "/wp-admin/", lambda s, b, h: s in (200, 302)),
    ("xmlrpc", "/xmlrpc.php", lambda s, b, h: s in (200, 405, 403)),
    ("wp-content", "/wp-content/", lambda s, b, h: s in (200, 403)),
    ("wp-includes", "/wp-includes/", lambda s, b, h: s in (200, 403)),
    ("readme", "/readme.html", lambda s, b, h: "WordPress" in b),
    ("license", "/license.txt", lambda s, b, h: s == 200),
    ("feed", "/feed/", lambda s, b, h: "rss" in b.lower()),
    ("wp-cron", "/wp-cron.php", lambda s, b, h: s in (200, 302)),
    ("install.php", "/wp-admin/install.php", lambda s, b, h: s == 200),
    ("version", "/?ver=1", lambda s, b, h: "ver=" in b),
]

PLUGINS = [
    "akismet", "contact-form-7", "wordfence", "woocommerce", "elementor",
    "revslider", "wordpress-seo", "jetpack", "w3-total-cache", "wp-super-cache",
    "backupbuddy", "gravityforms", "wpforms", "download-manager", "js_composer",
    "popup-anything-on-click", "data-tables-generator-by-supsystic",
    "wp-smart-preloader", "cf7-countries",
]

THEMES = ["twentytwentyfour", "twentytwentythree", "twentytwentytwo", "astra", "divi"]

VULNS = {
    "revslider": [
        ("CVE-2024-31348", "RevSlider Unauthenticated RCE", "/wp-admin/admin-ajax.php", {"action": "revslider_ajax_action"}),
        ("CVE-2024-30329", "RevSlider SQLi", "/wp-admin/admin-ajax.php", {"action": "revslider_do_ajax"}),
        ("CVE-2024-30913", "RevSlider File Upload", "/wp-admin/admin-ajax.php", {"action": "revslider_ajax_action", "client_action": "update_custom_css"}),
    ],
    "contact-form-7": [("CVE-2024-10533", "CF7 File Upload", "/wp-json/contact-form-7/v1/contact-forms", {})],
    "download-manager": [("CVE-2024-9750", "WPDM LFI", "/", {}), ("CVE-2024-7091", "WPDM SQLi", "/", {})],
    "js_composer": [("CVE-2024-3496", "WPBakery Stored XSS", "/wp-admin/admin-ajax.php", {})],
}


def scan_wp(target):
    base = ensure_url(target).rstrip("/")
    findings = []
    available = {}

    def _check(name, path, validator):
        u = f"{base}{path}"
        s, h, b = fetch(u)
        if s and validator(s, b, h):
            available[name] = u

    with ThreadPoolExecutor(max_workers=10) as ex:
        for n, p, v in CHECKS:
            ex.submit(_check, n, p, v)

    for name, url in available.items():
        sev = "HIGH" if name in ("xmlrpc", "wp-json/users", "wp-admin") else "INFO"
        findings.append({"name": f"WP: {name}", "severity": sev, "url": url})

    # Version
    if "version" in available:
        s, h, b = fetch(f"{base}/?ver=1")
        m = re.search(r'ver=(\d+\.\d+(?:\.\d+)?)', b)
        if m:
            findings.append({"name": f"WordPress {m.group(1)}", "severity": "INFO", "url": base})

    # Plugins
    def _check_plugin(slug):
        for ext in [f"/wp-content/plugins/{slug}/{slug}.php", f"/wp-content/plugins/{slug}/readme.txt"]:
            u = f"{base}{ext}"
            s, h, b = fetch(u)
            if s in (200, 403):
                return slug, u
        return None

    with ThreadPoolExecutor(max_workers=15) as ex:
        for r in ex.map(_check_plugin, PLUGINS):
            if r:
                slug, url = r
                findings.append({"name": f"Plugin: {slug}", "severity": "INFO", "url": url})
                # Check for known vulns
                if slug in VULNS:
                    for cve, desc, path, params in VULNS[slug]:
                        if path == "/":
                            findings.append({"name": f"{cve}: {desc}", "severity": "CRITICAL", "url": base, "evidence": f"{slug} installed"})
                        else:
                            qs = urlencode(params) if params else ""
                            u = f"{base}{path}?{qs}" if qs else f"{base}{path}"
                            s2, h2, b2 = fetch(u)
                            if s2 and s2 < 500:
                                findings.append({"name": f"{cve}: {desc}", "severity": "CRITICAL", "url": u, "evidence": f"Status: {s2}"})

    # XML-RPC methods
    if "xmlrpc" in available:
        xml = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
        s, h, b = http_post(f"{base}/xmlrpc.php", xml.encode(), {"Content-Type": "text/xml"})
        if s == 200 and "system.listMethods" in b:
            findings.append({"name": "XML-RPC Enabled", "severity": "MEDIUM", "url": f"{base}/xmlrpc.php", "evidence": "Brute force / pingback vector"})

    return findings
