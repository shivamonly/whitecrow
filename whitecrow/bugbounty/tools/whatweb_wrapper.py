import subprocess, shutil, time
import urllib.request
import ssl
import re


TECH_PATTERNS = [
    (r"wordpress", "WordPress"),
    (r"wp-content", "WordPress"),
    (r"drupal", "Drupal"),
    (r"joomla", "Joomla"),
    (r"laravel", "Laravel"),
    (r"csrf-token.*laravel", "Laravel"),
    (r"rails", "Ruby on Rails"),
    (r"django", "Django"),
    (r"flask", "Flask"),
    (r"express", "Express.js"),
    (r"next\.js", "Next.js"),
    (r"nuxt", "Nuxt.js"),
    (r"react", "React"),
    (r"angular", "Angular"),
    (r"vue", "Vue.js"),
    (r"nginx", "Nginx"),
    (r"apache", "Apache"),
    (r"cloudflare", "Cloudflare"),
    (r"php[/]?", "PHP"),
    (r"asp\.net", "ASP.NET"),
    (r"iis", "IIS"),
    (r"jquery", "jQuery"),
    (r"bootstrap", "Bootstrap"),
    (r"tailwind", "Tailwind CSS"),
    (r"shopify", "Shopify"),
    (r"magento", "Magento"),
    (r"woocommerce", "WooCommerce"),
]


def _detect_tech(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            headers = dict(r.headers)
            body = r.read().decode("utf-8", errors="ignore")
    except Exception:
        return [], []

    found = []
    for pattern, name in TECH_PATTERNS:
        if re.search(pattern, body, re.I) or re.search(pattern, str(headers), re.I):
            found.append(name)

    # Server header
    server = headers.get("Server", "")
    if server and server not in found:
        found.append(server)

    # X-Powered-By
    xpb = headers.get("X-Powered-By", "")
    if xpb and xpb not in found:
        found.append(xpb)

    return list(set(found)), headers


def run(target, output_dir):
    start = time.time()
    result_text = ""

    # Try whatweb binary first
    if shutil.which("whatweb"):
        try:
            r = subprocess.run(["whatweb", target, "--color=never"], capture_output=True, text=True, timeout=30)
            result_text = r.stdout.strip()
        except Exception:
            pass

    # Fallback: Python-based detection
    if not result_text:
        for proto in ["https", "http"]:
            url = f"{proto}://{target}"
            techs, headers = _detect_tech(url)
            if techs:
                result_text = f"{url} [{', '.join(techs)}]"
                break
        if not result_text:
            result_text = f"{target} [No technologies detected]"

    return {
        "status": "success",
        "result": result_text,
        "elapsed": round(time.time() - start, 2),
    }
