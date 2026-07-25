# WhiteCrow

**OSINT & Bug Bounty Scanner**

[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

---

## Install

```bash
git clone https://github.com/shivamonly/whitecrow.git
cd whitecrow
pip install -e .
```

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
