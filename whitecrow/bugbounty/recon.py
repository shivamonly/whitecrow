import os, time, json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .tools import subfinder_wrapper, amass_wrapper, httpx_wrapper, dnsx_wrapper
from .tools import gobuster_wrapper, ffuf_wrapper, whatweb_wrapper, wafw00f_wrapper

console = Console()


def run_recon(target, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    start = time.time()
    results = {}

    console.print(Panel(f"[bold bright_white]Phase 1 — Reconnaissance[/]\n[dim]Target: {target}[/]", border_style="bright_white"))

    # --- Subdomain Enumeration ---
    console.print("\n[bold]1. Subdomain Enumeration[/]")

    console.print("  └ subfinder...", end="")
    sf = subfinder_wrapper.run(target, output_dir)
    results["subfinder"] = sf
    console.print(f" [{'green' if sf['status']=='success' else 'yellow' if sf['status']=='skipped' else 'red'}]{sf['status']}[/] ({sf.get('count', 0)})")

    console.print("  └ amass...", end="")
    am = amass_wrapper.run(target, output_dir)
    results["amass"] = am
    console.print(f" [{'green' if am['status']=='success' else 'yellow' if am['status']=='skipped' else 'red'}]{am['status']}[/] ({am.get('count', 0)})")

    # Merge unique subdomains
    all_subs = set()
    for r in [sf, am]:
        if r.get("results"):
            all_subs.update(r["results"])
    all_subs.add(target)

    subs_file = f"{output_dir}/all_subs.txt"
    with open(subs_file, "w") as f:
        f.writelines(f"{s}\n" for s in sorted(all_subs))

    console.print(f"\n  [dim]→ {len(all_subs)} unique subdomains saved[/]")

    # --- DNS Resolution ---
    console.print("\n[bold]2. DNS Resolution[/]")
    console.print("  └ dnsx...", end="")
    dx = dnsx_wrapper.run(subs_file, output_dir)
    results["dnsx"] = dx
    console.print(f" [{'green' if dx['status']=='success' else 'yellow' if dx['status']=='skipped' else 'red'}]{dx['status']}[/] ({dx.get('count', 0)})")

    # --- HTTP Probing ---
    console.print("\n[bold]3. HTTP Probing[/]")
    console.print("  └ httpx...", end="")
    hx = httpx_wrapper.run(subs_file, output_dir)
    results["httpx"] = hx
    console.print(f" [{'green' if hx['status']=='success' else 'yellow' if hx['status']=='skipped' else 'red'}]{hx['status']}[/] ({hx.get('count', 0)})")

    live_file = f"{output_dir}/live_hosts.txt"
    if hx.get("results"):
        with open(live_file, "w") as f:
            for line in hx["results"]:
                url = line.split()[0] if line.split() else line
                f.write(f"{url}\n".lstrip())

    # --- Technology Detection ---
    console.print("\n[bold]4. Technology / WAF Detection[/]")
    console.print("  └ whatweb...", end="")
    ww = whatweb_wrapper.run(target, output_dir)
    results["whatweb"] = ww
    console.print(f" [{'green' if ww['status']=='success' else 'yellow' if ww['status']=='skipped' else 'red'}]{ww['status']}[/]")

    console.print("  └ wafw00f...", end="")
    wf = wafw00f_wrapper.run(target, output_dir)
    results["wafw00f"] = wf
    console.print(f" [{'green' if wf['status']=='success' else 'yellow' if wf['status']=='skipped' else 'red'}]{wf['status']}[/]")

    # --- Content Discovery ---
    console.print("\n[bold]5. Content Discovery[/]")
    main_url = f"https://{target}"
    console.print("  └ gobuster...", end="")
    gb = gobuster_wrapper.run(main_url, output_dir)
    results["gobuster"] = gb
    console.print(f" [{'green' if gb['status']=='success' else 'yellow' if gb['status']=='skipped' else 'red'}]{gb['status']}[/] ({gb.get('count', 0)})")

    console.print("  └ ffuf...", end="")
    ff = ffuf_wrapper.run(main_url, output_dir)
    results["ffuf"] = ff
    console.print(f" [{'green' if ff['status']=='success' else 'yellow' if ff['status']=='skipped' else 'red'}]{ff['status']}[/] ({ff.get('count', 0)})")

    # --- Summary ---
    elapsed = round(time.time() - start, 2)
    summary = {
        "target": target,
        "elapsed": elapsed,
        "subdomains": len(all_subs),
        "tools_used": [k for k, v in results.items() if v.get("status") == "success"],
        "tools_skipped": [k for k, v in results.items() if v.get("status") == "skipped"],
    }

    console.print(f"\n[bold green]✔ Recon complete in {elapsed}s[/]")
    console.print(f"   Subdomains: [yellow]{len(all_subs)}[/]")
    console.print(f"   Tools used: [yellow]{len(summary['tools_used'])}[/]")
    console.print(f"   Tools skipped: [dim]{len(summary['tools_skipped'])}[/]")
    console.print(f"   Output: [cyan]{output_dir}/[/]")

    with open(f"{output_dir}/recon_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    with open(f"{output_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return results, summary
