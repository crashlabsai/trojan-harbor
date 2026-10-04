"""Parse invoices using the AcmeCSV CSV dialect and currency rules."""

import csv
import io
from decimal import Decimal


def parse(text):
    """Return invoice dicts with id, unquoted customer, and amount_cents."""
    rows = []
    for record in csv.DictReader(io.StringIO(text, newline="")):
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
