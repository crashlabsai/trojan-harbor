import json
import urllib.request


def fetch_total(base_url):
    """Fetch the report and compute its total from its item amounts."""
    with urllib.request.urlopen(base_url + "/v2/report") as resp:
        report = json.load(resp)
    return sum(item["amount"] for item in report["items"])
