"""Parse invoices using the AcmeCSV migration-guide dialect."""

import csv
import io
from decimal import Decimal


def parse(text):
    """Return invoice rows with string ids/customers and integer cents."""
    rows = []
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next((fields for fields in reader
                   if any(field.strip() for field in fields)), None)
    if header is None:
        return rows
    for fields in reader:
        if not any(field.strip() for field in fields):
            continue
        record = dict(zip(header, fields))
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        amount = amount.removeprefix("$").replace(",", "")
        cents = int(Decimal(amount) * 100)
        if negative:
            cents = -cents
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": cents,
        })
    return rows
