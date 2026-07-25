import requests
import re
import json


def investigate(phone):
    cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone)
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    raw = cleaned.replace("+", "")
    result = {"phone": phone, "e164": cleaned, "country": None, "carrier": None, "line_type": None, "valid": False, "messaging": {}}

    # country detection from prefix
    prefixes = {
        "1": "US/CA", "7": "RU", "20": "EG", "27": "ZA", "30": "GR",
        "31": "NL", "32": "BE", "33": "FR", "34": "ES", "36": "HU",
        "39": "IT", "40": "RO", "41": "CH", "43": "AT", "44": "UK",
        "45": "DK", "46": "SE", "47": "NO", "48": "PL", "49": "DE",
        "51": "PE", "52": "MX", "53": "CU", "54": "AR", "55": "BR",
        "56": "CL", "57": "CO", "58": "VE", "60": "MY", "61": "AU",
        "62": "ID", "63": "PH", "64": "NZ", "65": "SG", "66": "TH",
        "81": "JP", "82": "KR", "84": "VN", "86": "CN", "90": "TR",
        "91": "IN", "92": "PK", "93": "AF", "94": "LK", "95": "MM",
        "98": "IR", "212": "MA", "213": "DZ", "216": "TN", "218": "LY",
        "220": "GM", "221": "SN", "222": "MR", "223": "ML", "224": "GN",
        "225": "CI", "226": "BF", "227": "NE", "228": "TG", "229": "BJ",
        "230": "MU", "231": "LR", "232": "SL", "233": "GH", "234": "NG",
        "235": "TD", "236": "CF", "237": "CM", "238": "CV", "239": "ST",
        "240": "GQ", "241": "GA", "242": "CG", "243": "CD", "244": "AO",
        "245": "GW", "246": "IO", "247": "AC", "248": "SC", "249": "SD",
        "250": "RW", "251": "ET", "252": "SO", "253": "DJ", "254": "KE",
        "255": "TZ", "256": "UG", "257": "BI", "258": "MZ", "260": "ZM",
        "261": "MG", "262": "RE", "263": "ZW", "264": "NA", "265": "MW",
        "266": "LS", "267": "BW", "268": "SZ", "269": "KM", "290": "SH",
        "291": "ER", "297": "AW", "298": "FO", "299": "GL", "350": "GI",
        "351": "PT", "352": "LU", "353": "IE", "354": "IS", "355": "AL",
        "356": "MT", "357": "CY", "358": "FI", "359": "BG", "370": "LT",
        "371": "LV", "372": "EE", "373": "MD", "374": "AM", "375": "BY",
        "376": "AD", "377": "MC", "378": "SM", "379": "VA", "380": "UA",
        "381": "RS", "382": "ME", "385": "HR", "386": "SI", "387": "BA",
        "389": "MK", "420": "CZ", "421": "SK", "423": "LI", "500": "FK",
        "501": "BZ", "502": "GT", "503": "SV", "504": "HN", "505": "NI",
        "506": "CR", "507": "PA", "508": "PM", "509": "HT", "590": "GP",
        "591": "BO", "592": "GY", "593": "EC", "594": "GF", "595": "PY",
        "596": "MQ", "597": "SR", "598": "UY", "599": "CW", "670": "TL",
        "672": "NF", "673": "BN", "674": "NR", "675": "PG", "676": "TO",
        "677": "SB", "678": "VU", "679": "FJ", "680": "PW", "681": "WF",
        "682": "CK", "683": "NU", "685": "WS", "686": "KI", "687": "NC",
        "688": "TV", "689": "PF", "690": "TK", "691": "FM", "692": "MH",
        "850": "KP", "852": "HK", "853": "MO", "855": "KH", "856": "LA",
        "880": "BD", "886": "TW", "960": "MV", "961": "LB", "962": "JO",
        "963": "SY", "964": "IQ", "965": "KW", "966": "SA", "967": "YE",
        "968": "OM", "970": "PS", "971": "AE", "972": "IL", "973": "BH",
        "974": "QA", "975": "BT", "976": "MN", "977": "NP", "992": "TJ",
        "993": "TM", "994": "AZ", "995": "GE", "996": "KG", "998": "UZ",
    }
    for k in sorted(prefixes.keys(), key=len, reverse=True):
        if raw.startswith(k):
            result["country"] = prefixes[k]
            break

    # local validation (regex + length)
    n_numeric = re.sub(r"\D", "", raw)
    country_digit_count = {"1": 10, "7": 10, "20": 9, "33": 9, "34": 9,
                           "39": 10, "44": 10, "49": 10, "52": 10, "55": 10,
                           "61": 9, "62": 10, "63": 10, "64": 9, "65": 8,
                           "81": 10, "82": 10, "86": 11, "90": 10, "91": 10,
                           "92": 10, "93": 9, "94": 9, "95": 8, "98": 10,
                           "212": 9, "213": 9, "216": 8, "218": 9,
                           "234": 10, "254": 9, "255": 9, "256": 9,
                           "260": 9, "263": 9, "264": 9, "265": 8,
                           "351": 9, "352": 8, "353": 9, "354": 7, "355": 8,
                           "356": 8, "357": 8, "358": 9, "359": 8,
                           "370": 8, "371": 8, "372": 7, "373": 8, "374": 8,
                           "375": 9, "380": 9, "381": 8, "385": 8, "386": 8,
                           "387": 8, "389": 8, "420": 9, "421": 9}
    expected = 10
    for k in sorted(country_digit_count.keys(), key=len, reverse=True):
        if n_numeric.startswith(k):
            expected = country_digit_count[k]
            break
    result["valid"] = len(n_numeric) == len(str(int(n_numeric))) and len(n_numeric[len(list(prefixes.keys())[0]):]) >= expected - 2

    # local carrier detection for common prefixes
    carriers = {
        "91": {
            "98": "Airtel", "99": "Airtel", "97": "Airtel",
            "96": "Airtel", "95": "Airtel",
            "93": "Jio", "932": "Jio", "933": "Jio", "934": "Jio",
            "935": "Jio", "936": "Jio", "937": "Jio",
            "90": "Vodafone Idea", "91": "Vodafone Idea",
            "89": "BSNL", "94": "BSNL",
            "70": "Jio", "73": "Jio", "74": "Jio", "75": "Jio",
            "76": "Jio", "77": "Jio", "78": "Jio", "79": "Jio",
            "80": "Airtel", "81": "Airtel", "82": "Airtel",
            "83": "Airtel", "84": "Airtel", "85": "Airtel",
            "86": "Airtel", "87": "Airtel", "88": "Airtel",
            "99": "Airtel",
        },
        "7": {
            "903": "Beeline", "905": "Beeline", "906": "Beeline",
            "909": "Beeline", "960": "Beeline", "961": "Beeline",
            "962": "Beeline", "963": "Beeline", "964": "Beeline",
            "965": "Beeline", "966": "Beeline", "967": "Beeline",
            "968": "Beeline", "969": "Beeline",
            "916": "MTS", "917": "MTS", "918": "MTS", "919": "MTS",
            "910": "MTS", "911": "MTS", "912": "MTS", "913": "MTS",
            "914": "MTS", "915": "MTS",
            "925": "Megafon", "926": "Megafon", "927": "Megafon",
            "928": "Megafon", "929": "Megafon", "930": "Megafon",
            "931": "Megafon", "932": "Megafon", "933": "Megafon",
            "934": "Megafon", "935": "Megafon", "936": "Megafon",
            "937": "Megafon", "938": "Megafon", "999": "Megafon",
            "951": "Tele2", "952": "Tele2", "953": "Tele2",
            "954": "Tele2", "955": "Tele2", "956": "Tele2",
            "957": "Tele2", "958": "Tele2", "959": "Tele2",
            "977": "Yota", "978": "Yota", "979": "Yota",
        },
        "1": {
            "201": "Verizon", "202": "Verizon", "203": "Verizon",
            "212": "AT&T", "213": "AT&T", "214": "AT&T",
            "310": "T-Mobile", "311": "T-Mobile", "312": "T-Mobile",
            "415": "AT&T", "416": "AT&T", "510": "AT&T",
            "612": "T-Mobile", "617": "Verizon", "619": "AT&T",
            "646": "Verizon", "650": "AT&T", "702": "AT&T",
            "718": "Verizon", "732": "Verizon", "773": "AT&T",
            "786": "T-Mobile", "800": "Toll-Free", "808": "Hawaii",
            "818": "AT&T", "832": "AT&T", "845": "Verizon",
            "858": "AT&T", "860": "AT&T", "866": "Toll-Free",
            "877": "Toll-Free", "888": "Toll-Free", "900": "Premium",
            "909": "AT&T", "914": "Verizon", "916": "AT&T",
            "917": "Verizon", "919": "AT&T", "925": "AT&T",
            "949": "AT&T", "954": "AT&T", "970": "AT&T",
            "972": "AT&T", "973": "Verizon", "978": "Verizon",
        },
        "44": {
            "77": "Vodafone", "78": "Vodafone", "79": "Vodafone",
            "74": "EE", "75": "EE", "73": "EE",
            "71": "Orange", "72": "Orange",
        },
    }
    detected_carrier = None
    for cc, prefixes in carriers.items():
        if n_numeric.startswith(cc):
            rest = n_numeric[len(cc):]
            carr = prefixes.get(rest[:3]) or prefixes.get(rest[:2]) or prefixes.get(rest[:1])
            if carr:
                detected_carrier = carr
                break
    if detected_carrier:
        result["carrier"] = detected_carrier
        result["line_type"] = "mobile"

    # messaging platform checks
    try:
        r = requests.get(f"https://wa.me/{raw}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8, allow_redirects=False)
        result["messaging"]["whatsapp"] = r.status_code in (200, 301, 302, 307)
    except Exception:
        result["messaging"]["whatsapp"] = None

    try:
        r = requests.get(f"https://t.me/{raw}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        result["messaging"]["telegram"] = r.status_code == 200
    except Exception:
        result["messaging"]["telegram"] = None

    try:
        r = requests.get(f"https://signal.me/#p/{raw}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        result["messaging"]["signal"] = r.status_code != 404
    except Exception:
        result["messaging"]["signal"] = None

    try:
        r = requests.get(f"https://viber.com/chat?number={raw}",
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        result["messaging"]["viber"] = r.status_code == 200
    except Exception:
        result["messaging"]["viber"] = None

    # google dork for phone
    try:
        r = requests.get(f"https://www.google.com/search?q=%22{cleaned}%22&num=5",
                        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}, timeout=8)
        if r.status_code == 200:
            links = re.findall(r'href="https?://([^"]+)"', r.text)
            result["exposure_urls"] = list(set(links))[:5]
    except Exception:
        pass

    return result
