import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter/X": "https://x.com/{}",
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
    "Mastodon.social": "https://mastodon.social/@{}",
    "VK": "https://vk.com/{}",
    "Facebook": "https://facebook.com/{}",
    "About.me": "https://about.me/{}",
    "AngelList": "https://angel.co/u/{}",
    "Behance": "https://behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "Flickr": "https://flickr.com/people/{}",
    "Gravatar": "https://gravatar.com/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "MixCloud": "https://mixcloud.com/{}",
    "OK": "https://ok.ru/{}",
    "Patreon": "https://patreon.com/{}",
    "ProductHunt": "https://producthunt.com/@{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Trello": "https://trello.com/{}",
    "Wattpad": "https://wattpad.com/user/{}",
    "Weibo": "https://weibo.com/{}",
    "Xing": "https://xing.com/profile/{}",
    "Academia": "https://academia.edu/{}",
    "AppleDev": "https://developer.apple.com/forums/profile/{}",
    "AskFM": "https://ask.fm/{}",
    "Badoo": "https://badoo.com/en/{}",
    "Bandcamp": "https://bandcamp.com/{}",
    "Blogger": "https://{}.blogspot.com",
    "Canva": "https://canva.com/{}",
    "Codecademy": "https://codecademy.com/profiles/{}",
    "Coderwall": "https://coderwall.com/{}",
    "Codewars": "https://codewars.com/users/{}",
    "Coub": "https://coub.com/{}",
    "Cracked": "https://cracked.com/members/{}",
    "Crevado": "https://crevado.com/{}",
    "devRant": "https://devrant.com/users/{}",
    "Discogs": "https://discogs.com/user/{}",
    "Disqus": "https://disqus.com/by/{}",
    "eBay": "https://ebay.com/usr/{}",
    "Ello": "https://ello.co/{}",
    "Etsy": "https://etsy.com/shop/{}",
    "EyeEm": "https://eyeem.com/u/{}",
    "Fiverr": "https://fiverr.com/{}",
    "Flipboard": "https://flipboard.com/@{}",
    "Freelancer": "https://freelancer.com/u/{}",
    "Giphy": "https://giphy.com/{}",
    "Goodreads": "https://goodreads.com/{}",
    "Gumroad": "https://gumroad.com/{}",
    "HackTheBox": "https://forum.hackthebox.com/u/{}/summary",
    "iMDB": "https://imdb.com/user/{}",
    "Imgur": "https://imgur.com/user/{}",
    "Issuu": "https://issuu.com/{}",
    "Itch.io": "https://{}.itch.io",
    "Kickstarter": "https://kickstarter.com/profile/{}",
    "Kongregate": "https://kongregate.com/accounts/{}",
    "Last.fm": "https://last.fm/user/{}",
    "Letterboxd": "https://letterboxd.com/{}",
    "LiveJournal": "https://{}.livejournal.com",
    "MyAnimeList": "https://myanimelist.net/profile/{}",
    "MySpace": "https://myspace.com/{}",
    "NameMC": "https://namemc.com/profile/{}",
    "Newgrounds": "https://{}.newgrounds.com",
    "NPM": "https://npmjs.com/~{}",
    "Periscope": "https://periscope.tv/{}",
    "PhoneHouse": "https://phonehouse.es/{}",
    "Plurk": "https://plurk.com/{}",
    "PokemonShowdown": "https://pokemonshowdown.com/users/{}",
    "Pypi": "https://pypi.org/user/{}",
    "Quizlet": "https://quizlet.com/{}",
    "Quora": "https://quora.com/profile/{}",
    "Ravelry": "https://ravelry.com/people/{}",
    "Roblox": "https://roblox.com/user/{}",
    "Rumble": "https://rumble.com/user/{}",
    "Scribd": "https://scribd.com/{}",
    "Signal": "https://signal.me/#p/{}",
    "Skype": "https://join.skype.com/invite/{}",
    "SlideShare": "https://slideshare.net/{}",
    "Smule": "https://smule.com/{}",
    "Speedrun": "https://speedrun.com/user/{}",
    "Splice": "https://splice.com/{}",
    "Sporcle": "https://sporcle.com/user/{}/plays",
    "Strava": "https://strava.com/athletes/{}",
    "TeamTreehouse": "https://teamtreehouse.com/{}",
    "Tinder": "https://tinder.com/@{}",
    "TryHackMe": "https://tryhackme.com/p/{}",
    "Tumblr": "https://{}.tumblr.com",
    "Upwork": "https://upwork.com/freelancers/~{}",
    "Vimeo": "https://vimeo.com/{}",
    "VSCO": "https://vsco.co/{}",
    "Wix": "https://{}.wixsite.com/website",
    "Wykop": "https://wykop.pl/ludzie/{}",
    "Zillow": "https://zillow.com/profile/{}",
    "Zone": "https://zone.msn.com/{}",
    "Carrd": "https://{}.carrd.co",
    "Linktree": "https://linktr.ee/{}",
    "Beacons": "https://beacons.ai/{}",
    "Bio.fm": "https://bio.fm/{}",
    "Bento": "https://bento.me/{}",
    "Taplink": "https://taplink.cc/{}",
    "Milkshake": "https://milkshake.app/{}",
    "Lnk.Bio": "https://lnk.bio/{}",
    "AllMyLinks": "https://allmylinks.com/{}",
    "FlowCode": "https://flowcode.com/{}",
    "Cardify": "https://cardify.co/{}",
}


def investigate(username):
    result = {"username": username, "profiles": [], "email_candidates": []}

    def _check(platform, url_template):
        try:
            url = url_template.format(username)
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
                            timeout=8, allow_redirects=True)
            if r.status_code == 200:
                return {"platform": platform, "url": url}
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = [ex.submit(_check, p, u) for p, u in PLATFORMS.items()]
        for f in as_completed(futures):
            try:
                r = f.result()
                if r:
                    result["profiles"].append(r)
            except Exception:
                pass

    result["count"] = len(result["profiles"])
    result["risk_score"] = min(len(result["profiles"]) * 2, 100)
    return result
