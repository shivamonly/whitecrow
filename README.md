# WhiteCrow

**OSINT & Bug Bounty Scanner**

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

## Usage

```bash
whitecrow target example.com         # Full recon
whitecrow attack example.com         # Full vuln scan
whitecrow wp example.com             # WordPress scan
whitecrow bypass403 example.com/admin # 403 bypass
whitecrow email user@example.com     # Email OSINT
whitecrow username johndoe           # Username search
```

## Modes

`target` `attack` `subdomain` `tech` `waf` `cdn` `content` `js` `sqli` `xss` `ssrf` `lfi` `cmdi` `idor` `graphql` `api` `wp` `bypass403` `bypasswaf` `email` `phone` `username` `exploit` `exploits`

---

## Disclaimer

This tool is for educational purposes only. You must have explicit written permission before testing any system.
