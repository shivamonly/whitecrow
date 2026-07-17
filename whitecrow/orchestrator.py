from __future__ import annotations
import time
import asyncio
from datetime import datetime

from .models import InvestigationResult, Overview, Identity, Contact, DigitalPresence
from .models import LocationData, BreachData, PhotoMetadata, TimelineEntry
from .input_detector import detect_and_parse
from .modules.email_investigator import investigate_email
from .modules.phone_investigator import investigate_phone
from .modules.username_investigator import investigate_username
from .modules.photo_investigator import investigate_photo
from .modules.social_cross_referencer import cross_reference


async def run_investigation(
    email: str | None = None,
    phone: str | None = None,
    username: str | None = None,
    photo_path: str | None = None,
) -> InvestigationResult:
    parsed = detect_and_parse(email, phone, username, photo_path)
    result = InvestigationResult(
        query={k: v for k, v in parsed["inputs"]},
        report_metadata={
            "generated_at": datetime.utcnow().isoformat(),
            "tools_used": [],
            "elapsed_seconds": 0.0,
            "version": "1.0.0",
        }
    )
    start = time.time()
    tasks = []

    for input_type, value in parsed["inputs"]:
        if input_type == "email":
            result.contact.email_addresses.append(value)
            tasks.append(investigate_email(value))
        elif input_type == "phone":
            result.contact.phone_numbers.append(value)
            tasks.append(investigate_phone(value))
        elif input_type == "username":
            tasks.append(investigate_username(value))
        elif input_type == "photo":
            tasks.append(investigate_photo(value))

    if tasks:
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        for module_results in all_results:
            if isinstance(module_results, Exception):
                continue
            for tool_name, tool_result in module_results.items():
                result.raw_findings[tool_name] = tool_result

    result = cross_reference(result)
    elapsed = time.time() - start
    result.report_metadata["elapsed_seconds"] = round(elapsed, 2)
    result.report_metadata["tools_used"] = list(result.raw_findings.keys())

    return result


def run_investigation_sync(
    email: str | None = None,
    phone: str | None = None,
    username: str | None = None,
    photo_path: str | None = None,
) -> InvestigationResult:
    return asyncio.run(
        run_investigation(
            email=email,
            phone=phone,
            username=username,
            photo_path=photo_path,
        )
    )
