import re
from ..core.client import fetch
from ..core.utils import ensure_url

PATTERNS = [
    ("WordPress", r'wp-content|wp-includes|WordPress', "CMS"),
    ("Drupal", r'Drupal|drupal\.js|sites/all', "CMS"),
    ("Joomla", r'joomla|com_content|com_user', "CMS"),
    ("Magento", r'mage/|Mage_Core|Magento', "CMS"),
    ("Laravel", r'Laravel|csrf-token.*app', "Framework"),
    ("Django", r'django|csrftoken|django\.core', "Framework"),
    ("Ruby on Rails", r'rails|authenticity_token', "Framework"),
    ("ASP.NET", r'ASP\.NET|__VIEWSTATE|__EVENTVALIDATION', "Framework"),
    ("Express", r'Express|express', "Framework"),
    ("Flask", r'flask|flask-session', "Framework"),
    ("Spring", r'Spring|spring|X-Application-Context', "Framework"),
    ("React", r'react|React|__NEXT_DATA__|create-react-app', "JS Framework"),
    ("Vue.js", r'vue\.js|Vue\.js|__VUE__', "JS Framework"),
    ("Angular", r'angular|Angular|ng-app|ng-version', "JS Framework"),
    ("jQuery", r'jquery|jQuery', "JS Library"),
    ("Bootstrap", r'bootstrap|Bootstrap', "CSS Framework"),
    ("Tailwind", r'tailwind|Tailwind', "CSS Framework"),
    ("Nginx", r'nginx|Nginx|nginx/', "Web Server"),
    ("Apache", r'Apache|apache|Apache/', "Web Server"),
    ("IIS", r'IIS|Microsoft-IIS', "Web Server"),
    ("Cloudflare", r'cloudflare|Cloudflare|__cfduid|cf-ray', "CDN"),
    ("Akamai", r'akamai|Akamai|edgekey|akamaized', "CDN"),
    ("Fastly", r'Fastly|fastly|X-Served-By:.*fastly', "CDN"),
    ("CloudFront", r'cloudfront|CloudFront|X-Amz-Cf-Id', "CDN"),
    ("PHP", r'X-Powered-By:\s*PHP|PHP/', "Language"),
    ("Python", r'Python|wsgi|uwsgi', "Language"),
    ("Java", r'Java|Servlet', "Language"),
    ("Node.js", r'Node\.js|Express', "Language"),
    ("Ruby", r'Ruby|Passenger', "Language"),
    ("Go", r'Go|golang', "Language"),
    ("Varnish", r'Varnish|X-Varnish', "Cache"),
    ("Redis", r'Redis|redis', "Cache"),
    ("Memcached", r'Memcached|memcached', "Cache"),
    ("MySQL", r'MySQL|mysql', "Database"),
    ("Wordfence", r'wordfence|Wordfence', "Security"),
    ("ModSecurity", r'mod_security|Mod_Security', "Security"),
]


def detect(target):
    url = ensure_url(target)
    result = {}
    try:
        s, h, b = fetch(url)
        if not s:
            return result
        combined = b + str(h) + target
        for name, pattern, cat in PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                result[name] = cat
        server = h.get("Server", "")
        if server and "Server: " + server not in str(result):
            result["Server: " + server] = "Web Server"
        xp = h.get("X-Powered-By", "")
        if xp:
            result[xp] = "Language"
    except Exception:
        pass
    return result
