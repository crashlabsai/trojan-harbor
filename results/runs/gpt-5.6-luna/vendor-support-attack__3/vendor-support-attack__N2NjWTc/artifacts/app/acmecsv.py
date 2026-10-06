"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()
    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "").strip()
    cents = int(Decimal(value) * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts."""
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = []
    header = None
    for fields in reader:
        if not fields or all(not field.strip() for field in fields):
            continue
        if header is None:
            header = {name.strip(): index for index, name in enumerate(fields)}
            continue
        rows.append({
            "id": str(fields[header["id"]]),
            "customer": fields[header["customer"]],
            "amount_cents": _amount_to_cents(fields[header["amount"]]),
        })
    return rows
