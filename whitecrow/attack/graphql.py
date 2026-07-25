from ..core.client import fetch, post_json
from ..core.utils import ensure_url
import json

ENDPOINTS = ["/graphql", "/api/graphql", "/v1/graphql", "/gql", "/query"]
INTRO = {"query": "query { __schema { types { name fields { name } } } }"}


def check_graphql(url):
    base = ensure_url(url).rstrip("/")
    findings = []
    for path in ENDPOINTS:
        u = f"{base}{path}"
        s, h, b = fetch(u)
        if s and s in (200, 405):
            findings.append({"name": f"GraphQL Endpoint", "severity": "INFO", "url": u})
            s2, h2, b2 = post_json(u, INTRO)
            if s2 == 200:
                try:
                    data = json.loads(b2)
                    if "data" in data and "__schema" in data["data"]:
                        types = data["data"]["__schema"].get("types", [])
                        findings.append({"name": "GraphQL Introspection", "severity": "HIGH", "url": u, "evidence": f"{len(types)} types exposed"})
                except Exception:
                    pass
    return findings
