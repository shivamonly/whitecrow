from __future__ import annotations
from ..tools.sherlock_wrapper import run_sherlock
from ..tools.maigret_wrapper import run_maigret
from ..models import ToolResult


async def investigate_username(username: str, timeout: int = 60) -> dict[str, ToolResult]:
    results = {}

    sherlock_res = run_sherlock(username, timeout)
    results["sherlock"] = ToolResult(
        tool="Sherlock", status=sherlock_res["status"],
        result=sherlock_res, elapsed=0.0
    )

    maigret_res = run_maigret(username, timeout)
    results["maigret"] = ToolResult(
        tool="Maigret", status=maigret_res["status"],
        result=maigret_res, elapsed=0.0
    )

    return results
