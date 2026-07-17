# WhiteCrow

**Unified OSINT investigation tool** — input an email, phone number, username, or photo and get a consolidated dossier.

```bash
# Install
pip install whitecrow

# Or with all optional tools
pip install "whitecrow[all]"

# With web UI
pip install "whitecrow[web]"
```

## Quick Start

```bash
# CLI — single input
whitecrow --email target@example.com
whitecrow --phone +1234567890
whitecrow --username johndoe
whitecrow --photo /path/to/photo.jpg

# Combine inputs
whitecrow --email target@example.com --username johndoe

# Save output
whitecrow --username johndoe -o report.json --pretty

# Web UI (after installing web extras)
uvicorn whitecrow.api:app --host 0.0.0.0 --port 8000
```

## What It Does

| Input | Tools Used |
|-------|-----------|
| **Email** | holehe (120+ site checks), emailrep.io (reputation), theHarvester (domain recon), GHunt (Google profile ID, YouTube, Calendar, Maps), HIBP (breach lookup) |
| **Phone** | libphonenumber (country, carrier, location, type), WhatsApp/Telegram/Signal registration check |
| **Username** | Sherlock (400+ social networks), Maigret (2500+ sites) |
| **Photo** | ExifTool (EXIF metadata), Google Reverse Image Search, Yandex Reverse Image Search |

## Install from Git

```bash
git clone https://github.com/yourusername/whitecrow.git
cd whitecrow
pip install -e ".[all]"
whitecrow --username johndoe
```

## Web API

```bash
pip install "whitecrow[web]"
uvicorn whitecrow.api:app --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

API endpoints:
- `POST /api/v1/investigate` — form data: `email`, `phone`, `username`, `photo` (file)
- `GET /api/v1/investigate/{task_id}` — get JSON result
- `GET /report/{task_id}` — view HTML report

## Cross-Platform

Works on **Linux**, **macOS**, and **Windows**. System tools (exiftool, theHarvester) are detected automatically — if absent, their modules are skipped gracefully.

## Legal

This tool is intended **only** for authorized security assessments, CTFs, and investigations with explicit consent. Unauthorized use may violate applicable laws.
