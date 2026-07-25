# WhiteCrow

**OSINT & Reconnaissance Tool**

Cross-Platform: Linux / macOS / Windows

---

## Install

```bash
git clone https://github.com/shivamonly/whitecrow.git
cd whitecrow
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -e .
```

> **Kali Linux**: Use a virtual environment (as shown above) because system Python is externally managed.

After install, run `whitecrow help` to see the interface.

```
  ⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⠸⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  ⢣⠈⠻⣿⣷⣦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣄⠀⠀
  ⢸⣶⣄⡀⠉⡝⣽⣿⣾⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣧⠀⠀
  ⢰⠙⢿⣿⣷⣶⣏⣙⡛⠿⢿⣿⣿⣿⣶⣶⣀⣀⣰⣆⠀⢀⣰⣿⢏⡆
  ⠈⢷⣤⡈⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣯⠵⠂
  ⠀⠀⠻⣿⣷⣦⣤⣤⣈⣩⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣦⡷⠁⠀
  ⠀⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⠁⠀⠀⠀

  WhiteCrow v2.1.0 — OSINT & Reconnaissance Tool
  Run 'whitecrow help' to get started.
```

## Usage

```bash
whitecrow target example.com         # Standard recon
whitecrow deep example.com           # Deep recon (subdomains → ports → ASN → tech → content)
whitecrow subdomain example.com      # Subdomain enumeration (14 sources)
whitecrow portscan 1.2.3.4           # Port scan (320 ports)
whitecrow asn 1.2.3.4               # ASN / IP geo info
whitecrow iposint 1.2.3.4           # Full IP OSINT
whitecrow tech example.com           # Technology detection
whitecrow waf example.com            # WAF detection
whitecrow cdn example.com            # CDN detection
whitecrow content https://example.com # Content discovery (200+ paths)
whitecrow js https://example.com     # JavaScript analysis
whitecrow email user@example.com     # Email OSINT
whitecrow phone +1234567890          # Phone OSINT
whitecrow username johndoe           # Username search (100+ platforms)
```

## Modes

`target` `deep` `subdomain` `tech` `waf` `cdn` `content` `js` `portscan` `asn` `iposint` `email` `phone` `username`

---

## Disclaimer

This tool is for educational purposes only. You must have explicit written permission before testing any system.
