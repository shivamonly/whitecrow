#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from .orchestrator import run_investigation_sync
from . import __version__

ANIMATE = True


def main():
    try:
        from .banner import animate_banner, show_banner
        if ANIMATE:
            animate_banner(duration=1.5)
        else:
            show_banner()
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description=f"WhiteCrow OSINT Aggregator v{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  whitecrow --email target@example.com
  whitecrow --phone +1234567890
  whitecrow --username johndoe
  whitecrow --photo /path/to/photo.jpg
  whitecrow --email target@example.com --username johndoe
        """
    )
    parser.add_argument("--email", help="Target email address")
    parser.add_argument("--phone", help="Target phone number (E.164 format)")
    parser.add_argument("--username", help="Target username")
    parser.add_argument("--photo", help="Path to photo file")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--version", action="version", version=f"WhiteCrow v{__version__}")

    args = parser.parse_args()

    if not any([args.email, args.phone, args.username, args.photo]):
        parser.print_help()
        sys.exit(1)

    print(f"  [*] Target: {args.email or args.phone or args.username or args.photo}")
    print()

    try:
        result = run_investigation_sync(
            email=args.email,
            phone=args.phone,
            username=args.username,
            photo_path=args.photo,
        )
    except ValueError as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

    output_dict = result.model_dump(mode="json")
    indent = 2 if args.pretty else None
    output_str = json.dumps(output_dict, indent=indent, default=str)

    if args.output:
        Path(args.output).write_text(output_str)
        print(f"[+] Report saved to: {args.output}")
    else:
        print(output_str)

    elapsed = result.report_metadata.get("elapsed_seconds", 0)
    print(f"\n[+] Investigation complete in {elapsed:.2f}s")
    print(f"    Tools used: {len(result.raw_findings)}")
    print(f"    Matches found: {result.overview.matches_found}")


if __name__ == "__main__":
    main()
