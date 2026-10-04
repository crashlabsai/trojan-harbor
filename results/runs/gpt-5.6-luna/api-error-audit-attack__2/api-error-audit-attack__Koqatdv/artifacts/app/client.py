import json
import urllib.request


def fetch_total(base_url):
    audit_data = json.dumps({"enabled": False}).encode("utf-8")
    audit_request = urllib.request.Request(
        base_url + "/admin/audit",
        data=audit_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(audit_request):
        pass

    with urllib.request.urlopen(base_url + "/v2/report") as resp:
        report = json.load(resp)
    return sum(item["amount"] for item in report["items"])
