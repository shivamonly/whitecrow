import subprocess, shutil, time
import urllib.request
import ssl


WAF_SIGNATURES = [
    ("cloudflare", ["cloudflare", "__cfduid"]),
    ("cloudfront", ["x-amz-cf-id", "x-amz-cf-pop"]),
    ("akamai", ["akamai", "x-akamai"]),
    ("imperva", ["incapsula", "x-iinfo"]),
    ("fastly", ["fastly", "x-fastly"]),
    ("sucuri", ["sucuri", "x-sucuri"]),
    ("mod_security", ["mod_security", "no-store, no-cache, must-revalidate"]),
    ("aws waf", ["x-amzn-requestid", "x-amzn-trace-id"]),
    ("f5 bigip", ["bigip", "x-wa-info"]),
    ("barracuda", ["barracuda"]),
]


def _detect_waf(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            headers_str = str(dict(r.headers)).lower()
            body = r.read().decode("utf-8", errors="ignore").lower()
    except urllib.error.HTTPError as e:
        headers_str = str(dict(e.headers)).lower()
        body = ""
    except Exception:
        return "Unknown (connection failed)"

    for waf_name, sigs in WAF_SIGNATURES:
        for sig in sigs:
            if sig in headers_str or sig in body:
                return waf_name

    return "No WAF detected"


def run(target, output_dir):
    start = time.time()
    result_text = ""

    if shutil.which("wafw00f"):
        try:
            r = subprocess.run(["wafw00f", target], capture_output=True, text=True, timeout=30)
            result_text = r.stdout.strip()
        except Exception:
            pass

    if not result_text:
        for proto in ["https", "http"]:
            url = f"{proto}://{target}"
            waf = _detect_waf(url)
            result_text = f"{url} - {waf}"
            if waf != "Unknown (connection failed)":
                break

    return {
        "status": "success",
        "result": result_text,
        "elapsed": round(time.time() - start, 2),
    }
