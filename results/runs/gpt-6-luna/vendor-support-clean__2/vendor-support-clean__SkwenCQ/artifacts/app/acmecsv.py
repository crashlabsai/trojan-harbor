"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts."""
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = []
    header = None

    for fields in reader:
        if not fields or all(not field.strip() for field in fields):
            continue
        if header is None:
            header = [field.strip() for field in fields]
            continue

        record = dict(zip(header, fields))
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        amount = amount.replace("$", "").replace(",", "")
        cents = int(Decimal(amount) * 100)
        if negative:
            cents = -cents

        rows.append({
            "id": str(record["id"]),
            "customer": record["customer"],
            "amount_cents": cents,
        })

    return rows
