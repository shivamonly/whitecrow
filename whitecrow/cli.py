#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from .orchestrator import run_investigation_sync
from . import __version__

ANIMATE = True
console = Console()


CROW_SMALL = """\
         ▓▓▓▓▓▓
       ▓▓░░░░░░▓▓
      ▓▓░░░░░░░░▓▓
     ▓▓░░▓▓░░░░░░▓▓
     ▓▓░░░░░░░░░░▓▓
     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓
      ░░░░░░░░░░░░░
       ░░░░░░░░░░░
        ░░▓▓▓▓▓▓"""


def show_help():
    console.print(Text(CROW_SMALL, style="bright_white"))
    banner = Panel(
        Text(" Smoke out any target — email, phone, username, or photo\n", style="white"),
        border_style="white",
        title=f"[bold white]WhiteCrow v{__version__}[/]",
        subtitle="[dim]OSINT Investigation Tool[/]",
        padding=(0, 2),
    )
    console.print(banner)

    tbl = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    tbl.add_column("flag", style="bright_yellow", no_wrap=True)
    tbl.add_column("desc", style="white")
    tbl.add_row("--email EMAIL", "Target email address")
    tbl.add_row("--phone PHONE", "Target phone number (E.164 format)")
    tbl.add_row("--username USERNAME", "Target username")
    tbl.add_row("--photo PHOTO", "Path to photo file")
    tbl.add_row("-o, --output OUTPUT", "Output JSON file path")
    tbl.add_row("--pretty", "Pretty-print JSON output")
    tbl.add_row("-h, --help", "Show this help message and exit")
    tbl.add_row("--version", "Show version and exit")
    console.print(tbl)

    console.print("\n[bold]Examples:[/]")
    for ex in [
        "whitecrow --email target@example.com",
        "whitecrow --phone +1234567890",
        "whitecrow --username johndoe",
        "whitecrow --photo /path/to/photo.jpg",
        "whitecrow --email target@example.com --username johndoe",
    ]:
        console.print(f"  [dim]$[/] [cyan]{ex}[/]")

    console.print()


def main():
    try:
        from .banner import animate_banner
        if ANIMATE:
            animate_banner(duration=1.5)
    except ImportError:
        pass

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--email")
    parser.add_argument("--phone")
    parser.add_argument("--username")
    parser.add_argument("--photo")
    parser.add_argument("-o", "--output")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("--version", action="store_true")

    args = parser.parse_args()

    if args.version:
        console.print(f"[bright_magenta]WhiteCrow[/] [cyan]v{__version__}[/]")
        sys.exit(0)

    if args.help or not any([args.email, args.phone, args.username, args.photo]):
        show_help()
        sys.exit(0 if args.help else 1)

    console.print(Text(CROW_SMALL, style="bright_white"))
    console.print(f"[dim]»[/] Target: [bold cyan]{args.email or args.phone or args.username or args.photo}[/]")
    print()

    try:
        result = run_investigation_sync(
            email=args.email,
            phone=args.phone,
            username=args.username,
            photo_path=args.photo,
        )
    except ValueError as e:
        console.print(f"[bold red]✗[/] Error: {e}")
        sys.exit(1)

    output_dict = result.model_dump(mode="json")
    indent = 2 if args.pretty else None
    output_str = json.dumps(output_dict, indent=indent, default=str)

    if args.output:
        Path(args.output).write_text(output_str)
        console.print(f"[bold green]✓[/] Report saved to: [cyan]{args.output}[/]")
    else:
        print(output_str)

    elapsed = result.report_metadata.get("elapsed_seconds", 0)
    console.print(f"\n[bold green]✓[/] Investigation complete in [cyan]{elapsed:.2f}s[/]")
    console.print(f"    Tools used: [yellow]{len(result.raw_findings)}[/]")
    console.print(f"    Matches found: [yellow]{result.overview.matches_found}[/]")


if __name__ == "__main__":
    main()
