import os, time, json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .tools import subfinder_wrapper, amass_wrapper, httpx_wrapper, dnsx_wrapper
from .tools import gobuster_wrapper, ffuf_wrapper, whatweb_wrapper, wafw00f_wrapper
from .tools import nuclei_wrapper, attack_wrapper
from .report_generator import generate_report

console = Console()

DISCLAIMER = """[bold yellow]⚠ DISCLAIMER[/]
[dim]This tool is for [bold]educational purposes only[/].
You must have [bold]explicit written permission[/] before testing any system.
The developer is [bold]NOT responsible[/] for any misuse or damage caused.
Unauthorized testing may be illegal and result in criminal charges.[/]"""


def show_disclaimer():
    console.print(Panel(DISCLAIMER, border_style="yellow", padding=(1, 2)))
    try:
        console.input("[dim]Press Enter to acknowledge and continue...[/]")
    except (EOFError, KeyboardInterrupt):
        console.print("\n[red]Aborted.[/]")
        exit(1)


def run_recon(target, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    start = time.time()
    results = {}

    show_disclaimer()

    console.print()
    console.print(Panel(f"[bold bright_white]WhiteCrow Bug Bounty Scanner[/]\n[dim]Target: {target}[/]", border_style="bright_white"))

    # --- Phase 1: Subdomain Enumeration ---
    console.print("\n[bold cyan]Phase 1 — Subdomain Enumeration[/]")
    console.print("  └ subfinder...", end="")
    sf = subfinder_wrapper.run(target, output_dir)
    results["subfinder"] = sf
    console.print(f" [{'green' if sf['status']=='success' else 'yellow' if sf['status']=='skipped' else 'red'}]{sf['status']}[/] ({sf.get('count', 0)})")

    console.print("  └ amass...", end="")
    am = amass_wrapper.run(target, output_dir)
    results["amass"] = am
    console.print(f" [{'green' if am['status']=='success' else 'yellow' if am['status']=='skipped' else 'red'}]{am['status']}[/] ({am.get('count', 0)})")

    all_subs = set()
    for r in [sf, am]:
        if r.get("results"):
            all_subs.update(r["results"])
    all_subs.add(target)

    subs_file = f"{output_dir}/all_subs.txt"
    with open(subs_file, "w") as f:
        f.writelines(f"{s}\n" for s in sorted(all_subs))
    console.print(f"  [dim]→ {len(all_subs)} unique subdomains[/]")

    # --- Phase 2: DNS + HTTP Probing ---
    console.print("\n[bold cyan]Phase 2 — DNS & HTTP Probing[/]")
    console.print("  └ dnsx...", end="")
    dx = dnsx_wrapper.run(subs_file, output_dir)
    results["dnsx"] = dx
    console.print(f" [{'green' if dx['status']=='success' else 'yellow' if dx['status']=='skipped' else 'red'}]{dx['status']}[/] ({dx.get('count', 0)})")

    console.print("  └ httpx...", end="")
    hx = httpx_wrapper.run(subs_file, output_dir)
    results["httpx"] = hx
    console.print(f" [{'green' if hx['status']=='success' else 'yellow' if hx['status']=='skipped' else 'red'}]{hx['status']}[/] ({hx.get('count', 0)})")

    live_file = f"{output_dir}/live_hosts.txt"
    live_urls = []
    if hx.get("results"):
        with open(live_file, "w") as f:
            for line in hx["results"]:
                url = line.split()[0] if line.split() else line
                if url.startswith("http"):
                    live_urls.append(url)
                    f.write(f"{url}\n")

    # --- Phase 3: Technology Detection ---
    console.print("\n[bold cyan]Phase 3 — Technology Detection[/]")
    console.print("  └ whatweb...", end="")
    ww = whatweb_wrapper.run(target, output_dir)
    results["whatweb"] = ww
    console.print(f" [{'green' if ww['status']=='success' else 'yellow' if ww['status']=='skipped' else 'red'}]{ww['status']}[/]")

    console.print("  └ wafw00f...", end="")
    wf = wafw00f_wrapper.run(target, output_dir)
    results["wafw00f"] = wf
    console.print(f" [{'green' if wf['status']=='success' else 'yellow' if wf['status']=='skipped' else 'red'}]{wf['status']}[/]")

    # --- Phase 4: Content Discovery ---
    console.print("\n[bold cyan]Phase 4 — Content Discovery[/]")
    main_url = f"https://{target}"
    console.print("  └ gobuster...", end="")
    gb = gobuster_wrapper.run(main_url, output_dir)
    results["gobuster"] = gb
    console.print(f" [{'green' if gb['status']=='success' else 'yellow' if gb['status']=='skipped' else 'red'}]{gb['status']}[/] ({gb.get('count', 0)})")

    console.print("  └ ffuf...", end="")
    ff = ffuf_wrapper.run(main_url, output_dir)
    results["ffuf"] = ff
    console.print(f" [{'green' if ff['status']=='success' else 'yellow' if ff['status']=='skipped' else 'red'}]{ff['status']}[/] ({ff.get('count', 0)})")

    # --- Phase 5: Vulnerability Analysis (WAHH Ch.5-13) ---
    console.print("\n[bold cyan]Phase 5 — Vulnerability Analysis[/]")
    console.print("  └ Info Disclosure / Auth / CORS / SSRF...", end="")
    atk = attack_wrapper.run(target, output_dir)
    results["vulnerability_analysis"] = atk
    atk_count = atk.get("total_findings", 0)
    console.print(f" [{'green' if atk_count else 'yellow'}]{'found' if atk_count else 'none'}[/] ({atk_count} issues)")

    # Print sub-findings
    for category, cat_result in atk.get("results", {}).items():
        if cat_result.get("count", 0):
            console.print(f"    ├ {category}: [yellow]{cat_result['count']}[/] findings")

    # --- Phase 6: Automated Scanning ---
    console.print("\n[bold cyan]Phase 6 — Automated Scanning[/]")
    targets_to_scan = live_urls if live_urls else [main_url]
    vuln_results = []
    for scan_target in targets_to_scan[:5]:
        console.print(f"  └ nuclei ({scan_target})...", end="")
        nuc = nuclei_wrapper.run(scan_target, output_dir)
        tag = scan_target.split("://")[1].split("/")[0]
        results[f"nuclei_{tag}"] = nuc
        vuln_results.append(nuc)
        console.print(f" [{'green' if nuc['status']=='success' else 'yellow' if nuc['status']=='skipped' else 'red'}]{nuc['status']}[/] ({nuc.get('count', 0)} findings)")

    # --- Summary ---
    elapsed = round(time.time() - start, 2)
    total_vulns = sum(len(r.get("results", [])) for r in vuln_results)
    total_attack = atk.get("total_findings", 0)

    summary = {
        "target": target,
        "elapsed_seconds": elapsed,
        "subdomains_found": len(all_subs),
        "live_hosts": len(live_urls),
        "vulnerabilities_found": total_vulns,
        "attack_issues": total_attack,
        "tools_used": [k for k, v in results.items() if v.get("status") == "success"],
        "tools_skipped": [k for k, v in results.items() if v.get("status") == "skipped"],
        "output_dir": str(output_dir),
    }

    # Save results
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    with open(f"{output_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Generate engagement report
    report_path = generate_report(target, output_dir, results, summary)
    console.print(f"\n[dim]Engagement report: [cyan]{report_path}[/][/]")

    # Print summary table
    console.print()
    tbl = Table(title="Scan Summary", box=box.SIMPLE, border_style="bright_white")
    tbl.add_column("Metric", style="yellow")
    tbl.add_column("Value", style="white")
    tbl.add_row("Target", target)
    tbl.add_row("Duration", f"{elapsed:.2f}s")
    tbl.add_row("Subdomains", str(len(all_subs)))
    tbl.add_row("Live Hosts", str(len(live_urls)))
    tbl.add_row("Attack Issues", str(total_attack))
    tbl.add_row("Vulnerabilities", str(total_vulns))
    tbl.add_row("Tools Used", str(len(summary["tools_used"])))
    tbl.add_row("Report", str(output_dir))
    console.print(tbl)

    console.print(f"\n[dim]Report saved to: [cyan]{output_dir}/summary.json[/][/]")

    return results, summary
