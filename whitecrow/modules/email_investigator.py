from __future__ import annotations
from ..tools.holehe_wrapper import run_holehe
from ..tools.emailrep_wrapper import run_emailrep
from ..tools.theharvester_wrapper import run_theharvester
from ..tools.ghunt_wrapper import run_ghunt
from ..tools.hibp_wrapper import run_hibp, run_hibp_pastes
from ..models import ToolResult
from ..config import EMAILREP_API_KEY, HIBP_API_KEY


async def investigate_email(email: str, timeout: int = 30) -> dict[str, ToolResult]:
    results = {}

    holehe_res = run_holehe(email, timeout)
    results["holehe"] = ToolResult(
        tool="holehe", status=holehe_res["status"],
        result=holehe_res, elapsed=0.0
    )

    emailrep_res = run_emailrep(email, EMAILREP_API_KEY)
    results["emailrep"] = ToolResult(
        tool="emailrep.io", status=emailrep_res["status"],
        result=emailrep_res, elapsed=0.0
    )

    harvester_res = run_theharvester(email, timeout)
    results["theharvester"] = ToolResult(
        tool="theHarvester", status=harvester_res["status"],
        result=harvester_res, elapsed=0.0
    )

    ghunt_res = run_ghunt(email, timeout)
    results["ghunt"] = ToolResult(
        tool="GHunt", status=ghunt_res["status"],
        result=ghunt_res, elapsed=0.0
    )

    hibp_res = run_hibp(email, HIBP_API_KEY)
    results["hibp"] = ToolResult(
        tool="HaveIBeenPwned", status=hibp_res["status"],
        result=hibp_res, elapsed=0.0
    )

    pastes_res = run_hibp_pastes(email, HIBP_API_KEY)
    results["hibp_pastes"] = ToolResult(
        tool="HIBP_Pastes", status=pastes_res["status"],
        result=pastes_res, elapsed=0.0
    )

    return results
