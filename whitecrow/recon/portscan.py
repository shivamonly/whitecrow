import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 81, 110, 111, 135, 139, 143, 389, 443, 445,
    465, 587, 631, 993, 995, 1433, 1521, 2049, 2082, 2083, 2086, 2087,
    2095, 2096, 2181, 2375, 2376, 2483, 2484, 2525, 3000, 3128, 3306,
    3389, 3689, 3690, 4000, 4040, 4443, 4500, 5000, 5001, 5222, 5223,
    5432, 5555, 5631, 5632, 5800, 5900, 5901, 5984, 5985, 5986, 6379,
    6443, 6667, 6668, 6669, 7000, 7001, 7070, 7071, 8000, 8001, 8008,
    8009, 8010, 8020, 8021, 8030, 8040, 8042, 8050, 8060, 8069, 8070,
    8080, 8081, 8082, 8083, 8086, 8087, 8088, 8089, 8090, 8091, 8092,
    8093, 8094, 8095, 8096, 8097, 8098, 8099, 8100, 8180, 8181, 8200,
    8222, 8243, 8280, 8300, 8333, 8400, 8443, 8500, 8530, 8531, 8880,
    8887, 8888, 8889, 8983, 9000, 9001, 9002, 9030, 9040, 9050, 9060,
    9080, 9090, 9091, 9100, 9150, 9160, 9191, 9200, 9292, 9300, 9443,
    9500, 9600, 9700, 9800, 9869, 9876, 9900, 9999, 10000, 10001, 10009,
    10080, 11211, 12345, 15672, 16080, 16180, 16379, 17000, 17001,
    18080, 18200, 19000, 19001, 20000, 20001, 21000, 22222, 23456,
    25565, 25672, 27015, 27016, 27017, 27333, 28015, 28017, 30000,
    30704, 31337, 32400, 32764, 32768, 32769, 32770, 32771, 32772,
    32773, 32774, 32775, 32776, 32777, 32778, 32779, 32780, 32781,
    32782, 32783, 32784, 32785, 32786, 32787, 32788, 32789, 32790,
    32791, 32792, 32793, 32794, 32795, 32796, 32797, 32798, 32799,
    32800, 32801, 32802, 32803, 32804, 32805, 32806, 32807, 32808,
    32809, 32810, 32811, 32812, 32813, 32814, 32815, 32816, 32817,
    32818, 32819, 32820, 32821, 32822, 32823, 32824, 32825, 32826,
    32827, 32828, 32829, 32830, 32831, 32832, 32833, 32834, 32835,
    32836, 32837, 32838, 32839, 32840, 32841, 32842, 32843, 32844,
    32845, 32846, 32847, 32848, 32849, 32850,
]

WEB_PORTS = {80, 81, 443, 8080, 8443, 3000, 5000, 8000, 8888, 9090, 9443}


def scan(hostname, ports=None, workers=50, timeout=2):
    if ports is None:
        ports = COMMON_PORTS
    open_ports = []
    def _check(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((hostname, port))
            s.close()
            if result == 0:
                service = _guess_service(port)
                return {"port": port, "service": service, "is_web": port in WEB_PORTS}
        except Exception:
            pass
        return None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_check, p): p for p in ports}
        for f in as_completed(futures):
            r = f.result()
            if r:
                open_ports.append(r)
    return sorted(open_ports, key=lambda x: x["port"])


def _guess_service(port):
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 81: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC",
        139: "NetBIOS", 143: "IMAP", 389: "LDAP", 443: "HTTPS",
        445: "SMB", 465: "SMTPS", 587: "SMTP", 631: "IPP",
        993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
        2049: "NFS", 2082: "cPanel", 2083: "cPanel SSL", 2086: "WHM",
        2087: "WHM SSL", 2095: "WebMail", 2096: "WebMail SSL",
        2181: "ZooKeeper", 2375: "Docker", 2376: "Docker SSL",
        3000: "HTTP-Alt", 3128: "Squid", 3306: "MySQL", 3389: "RDP",
        3689: "DAAP", 4000: "HTTP-Alt", 4040: "HTTP-Alt",
        4443: "HTTPS-Alt", 4500: "IPsec", 5000: "HTTP-Alt",
        5001: "UPnP", 5222: "XMPP", 5432: "PostgreSQL", 5555: "ADB",
        5631: "pcAnywhere", 5800: "VNC", 5900: "VNC", 5901: "VNC",
        5984: "CouchDB", 5985: "WinRM", 5986: "WinRM SSL",
        6379: "Redis", 6443: "HTTPS-Alt", 6667: "IRC", 6668: "IRC",
        6669: "IRC", 7000: "HTTP-Alt", 7001: "WebLogic",
        7070: "HTTP-Alt", 8000: "HTTP-Alt", 8001: "HTTP-Alt",
        8008: "HTTP", 8009: "AJP", 8069: "Odoo", 8080: "HTTP-Proxy",
        8081: "HTTP-Alt", 8443: "HTTPS-Alt", 8888: "HTTP-Alt",
        9000: "HTTP-Alt", 9001: "Tor", 9040: "Tor", 9050: "Tor",
        9090: "HTTP-Alt", 9100: "JetDirect", 9200: "Elasticsearch",
        9300: "Elasticsearch", 9443: "HTTPS-Alt", 9876: "HTTP-Alt",
        9999: "HTTP-Alt", 10000: "Webmin", 11211: "Memcached",
        12345: "NetBus", 15672: "RabbitMQ", 16379: "Redis",
        17000: "HTTP-Alt", 27017: "MongoDB", 27018: "MongoDB",
        27019: "MongoDB", 28017: "MongoDB-Web", 31337: "BackOrifice",
        32400: "Plex", 32764: "Router", 49152: "Windows-RPC",
    }
    return services.get(port, "Unknown")
