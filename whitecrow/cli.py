import argparse
import sys
import time
from .banner import print_banner, BANNER
from . import __version__
from .core.output import phase, summary, info, good, warn, bad, finding, section

MODES = {
    "target":    "Full bug bounty recon (enum → probe → tech → content → vulns)",
    "attack":    "Full vulnerability scan (SQLi, XSS, SSRF, LFI, etc.)",
    "subdomain": "Subdomain enumeration only",
    "tech":      "Technology detection only",
    "content":   "Content discovery only",
    "waf":       "WAF detection only",
    "cdn":       "CDN detection only",
    "js":        "JavaScript analysis only",
    "sqli":      "SQL injection scan",
    "xss":       "XSS scan",
    "ssrf":      "SSRF check",
    "lfi":       "LFI/RFI check",
    "cmdi":      "Command injection check",
    "idor":      "IDOR discovery",
    "graphql":   "GraphQL introspection",
    "api":       "API endpoint discovery",
    "wp":        "WordPress vulnerability scan",
    "bypass403": "403 bypass techniques",
    "bypasswaf": "WAF bypass payloads",
    "email":     "Email OSINT",
    "phone":     "Phone OSINT",
    "username":  "Username search (36 platforms)",
    "exploit":   "Show exploit info",
    "exploits":  "List all exploits",
}

def show_help():
    print_banner()
    print(f"  WhiteCrow v{__version__} — OSINT & Bug Bounty Scanner\n")
    print(f"  Usage: whitecrow <mode> <target> [options]\n")
    print(f"  {'MODE':<12} {'DESCRIPTION'}")
    print(f"  {'-'*12} {'-'*50}")
    for m, d in MODES.items():
        print(f"  {m:<12} {d}")
    print(f"\n  Options:")
    print(f"  -o FILE       Save output to JSON file")
    print(f"  --threads N   Threads (default 20)")
    print(f"  --proxy FILE  Load proxy list from file")
    print(f"  --timeout N   Request timeout (default 10s)")
    print(f"  --no-color    Disable color output")
    print(f"\n  Examples:")
    print(f"  whitecrow target example.com")
    print(f"  whitecrow attack https://example.com -o scan.json")
    print(f"  whitecrow wp https://example.com")
    print(f"  whitecrow bypass403 https://example.com/admin")
    print(f"  whitecrow email user@example.com")
    print(f"  whitecrow username johndoe")

def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("mode", nargs="?", default="")
    p.add_argument("target", nargs="?", default="")
    p.add_argument("-o", "--output")
    p.add_argument("--threads", type=int, default=20)
    p.add_argument("--proxy")
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--no-color", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    p.add_argument("--version", action="store_true")
    args, _ = p.parse_known_args()

    if args.version:
        print(f"WhiteCrow v{__version__}")
        sys.exit(0)

    if args.no_color:
        from .core import output
        output.COLOR = False

    from .core import client
    client.THREADS = args.threads
    client.TIMEOUT = args.timeout
    if args.proxy:
        try:
            with open(args.proxy) as f:
                client.PROXY_LIST = [l.strip() for l in f if l.strip()]
            good("Proxy", f"Loaded {len(client.PROXY_LIST)} proxies")
        except Exception as e:
            bad("Proxy", f"Failed: {e}")

    mode = args.mode.lower()
    target = args.target

    if args.help or not mode or mode not in MODES:
        show_help()
        sys.exit(0 if args.help else 1)

    print_banner()

    t0 = time.time()

    if mode == "target":
        run_target(target, args)
    elif mode == "attack":
        run_attack(target, args)
    elif mode == "subdomain":
        run_subdomain(target, args)
    elif mode == "tech":
        run_tech(target, args)
    elif mode == "content":
        run_content(target, args)
    elif mode == "waf":
        run_waf(target, args)
    elif mode == "cdn":
        run_cdn(target, args)
    elif mode == "js":
        run_js(target, args)
    elif mode == "sqli":
        run_sqli(target, args)
    elif mode == "xss":
        run_xss(target, args)
    elif mode == "ssrf":
        run_ssrf(target, args)
    elif mode == "lfi":
        run_lfi(target, args)
    elif mode == "cmdi":
        run_cmdi(target, args)
    elif mode == "idor":
        run_idor(target, args)
    elif mode == "graphql":
        run_graphql(target, args)
    elif mode == "api":
        run_api(target, args)
    elif mode == "wp":
        run_wp(target, args)
    elif mode == "bypass403":
        run_bypass403(target, args)
    elif mode == "bypasswaf":
        run_bypasswaf(target, args)
    elif mode == "email":
        run_email(target, args)
    elif mode == "phone":
        run_phone(target, args)
    elif mode == "username":
        run_username(target, args)
    elif mode == "exploit":
        run_exploit(target, args)
    elif mode == "exploits":
        run_exploits()

    elapsed = time.time() - t0
    print(f"\n{''.join(['─']*50)}")
    print(f"  Done in {elapsed:.2f}s")

def run_target(target, args):
    from .recon.subdomain import enum
    from .recon.dns import resolve
    from .recon.httprobe import probe
    from .recon.tech import detect
    from .recon.waf import detect_waf
    from .recon.cdn import detect_cdn
    from .recon.content import discover
    from .recon.javascript import analyze

    phase(1, "Subdomain Enumeration")
    subs = enum(target)
    n = len(subs)
    good("Subdomains", f"{n} found")
    if n:
        for s in subs[:10]:
            info("sub", s)
        if n > 10:
            info("sub", f"... and {n-10} more")

    phase(2, "DNS & HTTP Probing")
    hosts = [target] + subs
    resolved = resolve(hosts)
    good("DNS", f"{len(resolved)} resolved")
    live = probe(list(resolved.keys()))
    good("HTTP", f"{len(live)} live")

    phase(3, "Technology Detection")
    t = detect(target)
    good("Tech", f"{len(t)} detected")
    for name, cat in t.items():
        info(name, cat)

    phase(4, "WAF & CDN")
    w = detect_waf(target)
    info("WAF", w.get("waf", "None"))
    c = detect_cdn(target)
    info("CDN", c.get("cdn", "None"))

    phase(5, "Content Discovery")
    for u in live[:3]:
        found = discover(u)
        good("Content", f"{len(found)} paths on {u}")
        for f in found[:5]:
            info(f['url'], f"HTTP {f['status']}")

    phase(6, "JavaScript Analysis")
    for u in live[:2]:
        j = analyze(u)
        if j:
            good("JS", f"{len(j)} findings on {u}")

    summary(target, 0, n, len(live), 0)

def run_attack(target, args):
    from .attack.disclosure import check
    from .attack.sqli import scan
    from .attack.xss import check_xss
    from .attack.ssrf import check_ssrf
    from .attack.lfi import check_lfi
    from .attack.cmdi import check_cmdi
    from .attack.idor import check_idor
    from .attack.cors import check_cors
    from .attack.graphql import check_graphql
    from .attack.api import check_api
    from .attack.wordpress import scan_wp

    results = {"target": target, "findings": []}

    phase(1, "Information Disclosure")
    d = check(target)
    for f in d:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("Disclosure", f"{len(d)} issues")

    phase(2, "CORS & Headers")
    c = check_cors(target)
    for f in c:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("CORS", f"{len(c)} issues")

    phase(3, "SQL Injection")
    s = scan(target)
    for f in s:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("SQLi", f"{len(s)} issues")

    phase(4, "XSS")
    x = check_xss(target)
    for f in x:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("XSS", f"{len(x)} issues")

    phase(5, "SSRF")
    r = check_ssrf(target)
    for f in r:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("SSRF", f"{len(r)} issues")

    phase(6, "LFI/RFI")
    l = check_lfi(target)
    for f in l:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("LFI", f"{len(l)} issues")

    phase(7, "Command Injection")
    m = check_cmdi(target)
    for f in m:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("CMDi", f"{len(m)} issues")

    phase(8, "IDOR")
    i = check_idor(target)
    for f in i:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("IDOR", f"{len(i)} issues")

    phase(9, "API Endpoints")
    a = check_api(target)
    for f in a:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("API", f"{len(a)} endpoints")

    phase(10, "GraphQL")
    g = check_graphql(target)
    for f in g:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("GraphQL", f"{len(g)} issues")

    phase(11, "WordPress")
    w = scan_wp(target)
    for f in w:
        finding(f["name"], f["url"], f["severity"])
        results["findings"].append(f)
    good("WordPress", f"{len(w)} issues")

    summary(target, 0, 0, 1, len(results["findings"]))

    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

def run_subdomain(target, args):
    from .recon.subdomain import enum
    subs = enum(target)
    for s in subs:
        print(s)
    if args.output:
        with open(args.output, "w") as f:
            for s in subs:
                f.write(s + "\n")

def run_tech(target, args):
    from .recon.tech import detect
    for name, cat in detect(target).items():
        print(f"{name}: {cat}")

def run_content(target, args):
    from .recon.content import discover
    for f in discover(target):
        print(f"{f['status']} {f['url']}")

def run_waf(target, args):
    from .recon.waf import detect_waf
    import json; print(json.dumps(detect_waf(target), indent=2))

def run_cdn(target, args):
    from .recon.cdn import detect_cdn
    import json; print(json.dumps(detect_cdn(target), indent=2))

def run_js(target, args):
    from .recon.javascript import analyze
    import json; print(json.dumps(analyze(target), indent=2))

def run_sqli(target, args):
    from .attack.sqli import scan
    for f in scan(target):
        print(f"{f.get('severity')}: {f.get('url')}")

def run_xss(target, args):
    from .attack.xss import check_xss
    for f in check_xss(target):
        print(f"{f.get('severity')}: {f.get('url')}")

def run_ssrf(target, args):
    from .attack.ssrf import check_ssrf
    import json; print(json.dumps(check_ssrf(target), indent=2))

def run_lfi(target, args):
    from .attack.lfi import check_lfi
    import json; print(json.dumps(check_lfi(target), indent=2))

def run_cmdi(target, args):
    from .attack.cmdi import check_cmdi
    import json; print(json.dumps(check_cmdi(target), indent=2))

def run_idor(target, args):
    from .attack.idor import check_idor
    import json; print(json.dumps(check_idor(target), indent=2))

def run_graphql(target, args):
    from .attack.graphql import check_graphql
    import json; print(json.dumps(check_graphql(target), indent=2))

def run_api(target, args):
    from .attack.api import check_api
    import json; print(json.dumps(check_api(target), indent=2))

def run_wp(target, args):
    from .attack.wordpress import scan_wp
    for f in scan_wp(target):
        print(f"{f.get('severity','')}: {f.get('name','')} - {f.get('url','')}")
    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(scan_wp(target), f, indent=2)

def run_bypass403(target, args):
    from .bypass.f403 import bypass
    for t, s in bypass(target).items():
        if s and isinstance(s, int) and s < 400:
            good("BYPASS", f"{t} → {s}")
        else:
            warn("BLOCKED", f"{t} → {s}")

def run_bypasswaf(target, args):
    from .bypass.waf import bypass_waf
    import json; print(json.dumps(bypass_waf(target), indent=2))

def run_email(target, args):
    from .osint.email import investigate
    import json; print(json.dumps(investigate(target), indent=2, default=str))

def run_phone(target, args):
    from .osint.phone import investigate
    import json; print(json.dumps(investigate(target), indent=2, default=str))

def run_username(target, args):
    from .osint.username import investigate
    result = investigate(target)
    for p in result.get("profiles", []):
        print(f"{p['platform']}: {p['url']}")

def run_exploit(target, args):
    from .exploits.database import get_exploit
    import json; print(json.dumps(get_exploit(target), indent=2))

def run_exploits():
    from .exploits.database import list_exploits
    for e in list_exploits():
        print(e)
