from __future__ import annotations
from ..tools.phonenumbers_wrapper import run_phonenumbers
from ..tools.messaging_checker import check_whatsapp, check_telegram, check_signal
from ..models import ToolResult


async def investigate_phone(phone: str, timeout: int = 30) -> dict[str, ToolResult]:
    results = {}

    pn_res = run_phonenumbers(phone, timeout)
    results["phonenumbers"] = ToolResult(
        tool="phonenumbers", status=pn_res["status"],
        result=pn_res, elapsed=0.0
    )

    wa_res = check_whatsapp(phone)
    results["whatsapp"] = ToolResult(
        tool="WhatsApp", status=wa_res["status"],
        result=wa_res, elapsed=0.0
    )

    tg_res = check_telegram(phone)
    results["telegram"] = ToolResult(
        tool="Telegram", status=tg_res["status"],
        result=tg_res, elapsed=0.0
    )

    sig_res = check_signal(phone)
    results["signal"] = ToolResult(
        tool="Signal", status=sig_res["status"],
        result=sig_res, elapsed=0.0
    )

    return results
