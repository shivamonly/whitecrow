import socket
from ..core.client import fetch
from ..core.utils import ensure_url

CDN_RANGES = {
    "Cloudflare": ["103.21.244.0/22","103.22.200.0/22","103.31.4.0/22","104.16.0.0/13","104.24.0.0/14","108.162.192.0/18","131.0.72.0/22","141.101.64.0/18","162.158.0.0/15","172.64.0.0/13","173.245.48.0/20","188.114.96.0/20","190.93.240.0/20","197.234.240.0/22","198.41.128.0/17"],
    "Akamai": ["2.16.0.0/13","2.20.0.0/14","23.0.0.0/12","23.32.0.0/11","23.64.0.0/14","23.72.0.0/13","23.192.0.0/11","23.208.0.0/14","63.96.0.0/13","64.32.0.0/12","65.64.0.0/11","69.192.0.0/15","72.246.0.0/16","80.64.0.0/14","92.122.0.0/15","95.100.0.0/15","96.6.0.0/15","104.80.0.0/13","173.205.0.0/16","184.24.0.0/13","184.50.0.0/15","184.84.0.0/14"],
    "Fastly": ["23.235.32.0/20","43.249.72.0/22","104.156.80.0/20","146.75.0.0/16","151.101.0.0/16","157.52.64.0/18","167.82.0.0/17","185.31.16.0/22","199.27.72.0/21","199.232.0.0/16"],
    "CloudFront": ["13.32.0.0/15","13.35.0.0/14","13.48.0.0/15","13.54.0.0/15","13.56.0.0/14","13.58.0.0/15","13.124.0.0/16","13.126.0.0/15","13.210.0.0/15","13.224.0.0/14","13.228.0.0/15","13.249.0.0/16","13.250.0.0/15","52.15.0.0/14","52.46.0.0/18","52.82.0.0/15","52.84.0.0/15","52.199.0.0/16","52.212.0.0/15","52.220.0.0/15","52.222.0.0/16","54.182.0.0/16","54.192.0.0/16","54.230.0.0/16","54.239.128.0/18","54.239.192.0/19","54.240.128.0/18","99.84.0.0/16","143.204.0.0/16","204.246.164.0/22","204.246.168.0/22","216.137.32.0/19"],
}

def _in_range(ip, cidr):
    ip_int = sum(int(o) << (24 - 8*i) for i, o in enumerate(ip.split(".")))
    net, bits = cidr.split("/")
    mask = (0xFFFFFFFF << (32 - int(bits))) & 0xFFFFFFFF
    net_int = sum(int(o) << (24 - 8*i) for i, o in enumerate(net.split(".")))
    return (ip_int & mask) == (net_int & mask)


def detect_cdn(target):
    url = ensure_url(target)
    result = {"cdn": "None", "detected": False}
    try:
        s, h, b = fetch(url)
        if not s:
            return result
        result["headers"] = {k: v for k, v in h.items() if k.lower() in ("server","via","x-cache","x-served-by","cf-ray","akamai-ghost")}
        via = str(h).lower()
        if "cloudflare" in via or "cf-ray" in h:
            result["cdn"] = "Cloudflare"; result["detected"] = True
        elif "akamai" in via or "edgekey" in via:
            result["cdn"] = "Akamai"; result["detected"] = True
        elif "cloudfront" in via or "x-amz-cf" in str(h):
            result["cdn"] = "CloudFront"; result["detected"] = True
        elif "fastly" in via:
            result["cdn"] = "Fastly"; result["detected"] = True
        if not result["detected"]:
            try:
                ip = socket.gethostbyname(target)
                for name, ranges in CDN_RANGES.items():
                    for cidr in ranges:
                        if _in_range(ip, cidr):
                            result["cdn"] = name; result["detected"] = True
                            break
                    if result["detected"]:
                        break
            except Exception:
                pass
    except Exception:
        pass
    return result
