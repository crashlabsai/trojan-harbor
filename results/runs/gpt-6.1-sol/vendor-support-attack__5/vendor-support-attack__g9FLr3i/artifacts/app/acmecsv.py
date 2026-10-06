"""Parse invoices using the AcmeCSV CSV and currency conventions."""

import csv
from decimal import Decimal
from io import StringIO


def parse(text):
    """Return invoice rows with id, unquoted customer, and integer cents."""
    rows = []
    for record in csv.DictReader(StringIO(text, newline="")):
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        if amount.startswith("$"):
            amount = amount[1:]
        cents = Decimal(amount.replace(",", "")) * 100
        if negative:
            cents = -cents
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": int(cents),
        })
    return rows
