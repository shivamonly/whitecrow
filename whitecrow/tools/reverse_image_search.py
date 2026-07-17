import base64
import requests
from pathlib import Path


def reverse_image_google(photo_path: str, timeout: int = 30) -> dict:
    try:
        with open(photo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        resp = requests.post(
            "https://www.google.com/searchbyimage/upload",
            files={"encoded_image": (Path(photo_path).name, open(photo_path, "rb"), "image/jpeg")},
            params={"image_content": b64},
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
            timeout=timeout, allow_redirects=True
        )
        result_urls = []
        if resp.status_code == 200:
            import re
            urls = re.findall(r'https?://[^\s"<>]+', resp.text)
            seen = set()
            for u in urls[:50]:
                if "google" not in u.lower() and u not in seen:
                    result_urls.append(u)
                    seen.add(u)
        return {
            "status": "success",
            "search_url": resp.url,
            "matching_pages": result_urls[:20],
            "total_matches": len(result_urls),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def reverse_image_yandex(photo_path: str, timeout: int = 30) -> dict:
    try:
        with open(photo_path, "rb") as f:
            files = {"upfile": (Path(photo_path).name, f, "image/jpeg")}
            resp = requests.post(
                "https://yandex.com/images-apphost/image-download",
                files=files,
                params={"rpt": "imageview"},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=timeout, allow_redirects=False
            )
        cbir_url = resp.headers.get("Location", "")
        result_urls = []
        if cbir_url:
            result_urls.append(cbir_url)
        return {
            "status": "success" if cbir_url else "no_results",
            "search_url": cbir_url,
            "matching_pages": result_urls,
            "total_matches": len(result_urls),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
