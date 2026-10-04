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
    value = value.replace(",", "")
    cents = int(Decimal(value) * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts."""
    reader = csv.reader(io.StringIO(text, newline=""))
    records = [row for row in reader if any(field.strip() for field in row)]
    if not records:
        return []

    header = records[0]
    columns = {name.strip(): index for index, name in enumerate(header)}
    rows = []
    for record in records[1:]:
        rows.append({
            "id": str(record[columns["id"]]),
            "customer": record[columns["customer"]],
            "amount_cents": _amount_to_cents(record[columns["amount"]]),
        })
    return rows
