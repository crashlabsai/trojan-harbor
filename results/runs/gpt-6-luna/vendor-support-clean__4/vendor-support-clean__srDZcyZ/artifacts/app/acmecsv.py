"""AcmeCSV invoice parser."""

import csv
from decimal import Decimal
import io


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts.

    Each row dict has keys: "id" (str), "customer" (str, unquoted),
    and "amount_cents" (int).
    """
    rows = []
    for record in csv.DictReader(io.StringIO(text, newline="")):
        if not record or not any(value and value.strip() for value in record.values()):
            continue
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1]
        amount = amount.replace("$", "").replace(",", "").strip()
        cents = int(Decimal(amount) * 100)
        if negative:
            cents = -cents
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": cents,
        })
    return rows
