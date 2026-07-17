<pre align="center">
        ▄▄▄
       █▓▓▓█
      █▓▓▓▓▓█
  ▄▄  █▓ ● ▓█  🚬
 █  █ █▓ V ▓█
 █  █ █▓   ▓█
 █  █ █▓▓▓▓▓█
  █  ██▓▓▓█
   █  █  █
     █  █
    ╱█  █╲
   ╱ █  █ ╲
</pre>

<h1 align="center">WhiteCrow</h1>
<p align="center"><strong>Smoke out any target</strong> — email, phone, username, or photo</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue">
  <img src="https://img.shields.io/badge/license-MIT-green">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey">
</p>

---

```bash
# Install
pip install whitecrow

# With all optional tools (sherlock, maigret, holehe, ghunt)
pip install "whitecrow[all]"
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

# Web UI
pip install "whitecrow[web]"
uvicorn whitecrow.api:app --host 0.0.0.0 --port 8000
```

## What It Does

| Input | Tools Used |
|-------|-----------|
| **Email** | holehe (121 site checks), emailrep.io (reputation), theHarvester (domain recon), GHunt (Google profile), HIBP (breach + paste lookup) |
| **Phone** | libphonenumber (country, carrier, location, type), WhatsApp/Telegram/Signal registration check |
| **Username** | Sherlock (400+ platforms), Maigret (2500+ sites) |
| **Photo** | ExifTool (EXIF/GPS metadata), Google + Yandex reverse image search |

## Install from Git

```bash
git clone https://github.com/shivamonly/whitecrow.git
cd whitecrow
pip install -e ".[all]"
whitecrow --username johndoe
```

## API

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/investigate` | Submit email, phone, username, or photo |
| `GET /api/v1/investigate/{task_id}` | Get JSON result |
| `GET /report/{task_id}` | View HTML report |

## Cross-Platform

Works on **Linux**, **macOS**, and **Windows**. System tools (exiftool, theHarvester) are detected automatically — if absent, their modules are skipped gracefully.

## Legal

For authorized security assessments, CTFs, and investigations with explicit consent only.
