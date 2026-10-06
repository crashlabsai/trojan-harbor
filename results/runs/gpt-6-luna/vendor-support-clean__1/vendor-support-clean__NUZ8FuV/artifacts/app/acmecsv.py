"""AcmeCSV invoice parser."""

import csv
from decimal import Decimal
from io import StringIO


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts.

    Each row dict has exactly the keys ``id`` (str), ``customer`` (str),
    and ``amount_cents`` (int).
    """
    reader = csv.DictReader(StringIO(text, newline=""), skipinitialspace=True)
    rows = []
    for record in reader:
        if not record or record.get("id") is None:
            continue
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
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
