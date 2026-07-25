from ..core.client import fetch
from ..core.utils import ensure_url

TARGETS = [
    ("AWS Metadata", "http://169.254.169.254/latest/meta-data/"),
    ("GCP Metadata", "http://metadata.google.internal/computeMetadata/v1/"),
    ("Azure Metadata", "http://169.254.169.254/metadata/instance"),
    ("DO Metadata", "http://169.254.169.254/metadata/v1.json"),
    ("Localhost:3306", "http://localhost:3306"),
    ("Localhost:6379", "http://localhost:6379"),
    ("Localhost:9200", "http://localhost:9200"),
    ("Localhost:2375", "http://localhost:2375"),
]


def check_ssrf(url):
    findings = []
    for name, target in TARGETS:
        s, h, b = fetch(target, timeout=5)
        if s and s < 400:
            findings.append({
                "name": f"SSRF: {name}",
                "severity": "CRITICAL",
                "url": target,
                "evidence": f"Status: {s}, Body: {b[:100]}"
            })
    return findings
