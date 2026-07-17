from __future__ import annotations
from ..tools.exiftool_wrapper import run_exiftool
from ..tools.reverse_image_search import reverse_image_google, reverse_image_yandex
from ..models import ToolResult


async def investigate_photo(photo_path: str, timeout: int = 30) -> dict[str, ToolResult]:
    results = {}

    exif_res = run_exiftool(photo_path, 15)
    results["exiftool"] = ToolResult(
        tool="ExifTool", status=exif_res["status"],
        result=exif_res, elapsed=0.0
    )

    google_res = reverse_image_google(photo_path, timeout)
    results["google_images"] = ToolResult(
        tool="Google Images", status=google_res["status"],
        result=google_res, elapsed=0.0
    )

    yandex_res = reverse_image_yandex(photo_path, timeout)
    results["yandex_images"] = ToolResult(
        tool="Yandex Images", status=yandex_res["status"],
        result=yandex_res, elapsed=0.0
    )

    return results
