"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts."""
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = []
    try:
        header = next(reader)
    except StopIteration:
        return rows

    columns = {name: index for index, name in enumerate(header)}
    for fields in reader:
        if not fields or not any(field.strip() for field in fields):
            continue
        row_id = fields[columns["id"]]
        customer = fields[columns["customer"]]
        amount_text = fields[columns["amount"]].strip()
        negative = amount_text.startswith("(") and amount_text.endswith(")")
        if negative:
            amount_text = amount_text[1:-1].strip()
        amount_text = amount_text.replace("$", "").replace(",", "")
        amount_cents = int(Decimal(amount_text) * 100)
        if negative:
            amount_cents = -amount_cents
        rows.append({
            "id": str(row_id),
            "customer": customer,
            "amount_cents": amount_cents,
        })
    return rows
