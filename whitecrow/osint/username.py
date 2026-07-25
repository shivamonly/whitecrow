import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://reddit.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Keybase": "https://keybase.io/{}",
    "Pinterest": "https://pinterest.com/{}",
    "Telegram": "https://t.me/{}",
    "YouTube": "https://youtube.com/@{}",
    "Twitch": "https://twitch.tv/{}",
    "TikTok": "https://tiktok.com/@{}",
    "LinkedIn": "https://linkedin.com/in/{}",
    "Snapchat": "https://snapchat.com/add/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Replit": "https://replit.com/@{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "BitBucket": "https://bitbucket.org/{}",
    "GitLab": "https://gitlab.com/{}",
    "HackerOne": "https://hackerone.com/{}",
    "Bugcrowd": "https://bugcrowd.com/{}",
    "WordPress": "https://{}.wordpress.com",
}


def investigate(username):
    result = {"username": username, "profiles": []}
    def _check(platform, url):
        try:
            r = requests.get(url.format(username),
                           headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if r.status_code == 200:
                return {"platform": platform, "url": url.format(username)}
        except Exception:
            pass
        return None
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = [ex.submit(_check, p, u) for p, u in PLATFORMS.items()]
        for f in as_completed(futures):
            try:
                r = f.result()
                if r:
                    result["profiles"].append(r)
            except Exception:
                pass
    result["count"] = len(result["profiles"])
    return result
