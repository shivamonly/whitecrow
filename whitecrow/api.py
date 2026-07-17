from __future__ import annotations
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .orchestrator import run_investigation
from .models import InvestigationResult
from .config import UPLOAD_DIR

templates_path = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

app = FastAPI(
    title="WhiteCrow OSINT Aggregator",
    version="1.0.0",
    description="Unified OSINT investigation API"
)

investigation_cache: dict[str, InvestigationResult] = {}


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@app.get("/api/v1/health")
async def health():
    return {"service": "WhiteCrow", "version": "1.0.0", "status": "ok"}


@app.post("/api/v1/investigate")
async def investigate(
    email: str = Form(None),
    phone: str = Form(None),
    username: str = Form(None),
    photo: UploadFile = File(None),
):
    if not any([email, phone, username, photo]):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least one of: email, phone, username, photo"}
        )

    photo_path = None
    if photo:
        ext = Path(photo.filename or "image.jpg").suffix
        dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
        content = await photo.read()
        dest.write_bytes(content)
        photo_path = str(dest)

    task_id = uuid.uuid4().hex

    try:
        result = await run_investigation(
            email=email,
            phone=phone,
            username=username,
            photo_path=photo_path,
        )
        investigation_cache[task_id] = result
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result.model_dump(mode="json")
        }
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get("/api/v1/investigate/{task_id}")
async def get_investigation(task_id: str):
    result = investigation_cache.get(task_id)
    if not result:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return {
        "task_id": task_id,
        "status": "completed",
        "result": result.model_dump(mode="json")
    }


@app.get("/report/{task_id}", response_class=HTMLResponse)
async def get_report(task_id: str, request: Request):
    result = investigation_cache.get(task_id)
    if not result:
        return HTMLResponse("<h1>Report not found</h1>", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "request": request,
            "result": result.model_dump(mode="json"),
        }
    )
