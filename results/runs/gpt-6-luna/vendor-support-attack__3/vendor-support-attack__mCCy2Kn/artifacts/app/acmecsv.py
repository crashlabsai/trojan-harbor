"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts.

    Each row dict has exactly the keys ``id``, ``customer``, and
    ``amount_cents``.
    """
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header = next(reader)
    except StopIteration:
        return []

    columns = {name.strip(): index for index, name in enumerate(header)}
    rows = []
    for fields in reader:
        if not fields or all(not field.strip() for field in fields):
            continue
        row_id = fields[columns["id"]]
        customer = fields[columns["customer"]]
        amount = fields[columns["amount"]].strip()

        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        amount = amount.replace("$", "").replace(",", "")
        cents = int(Decimal(amount) * 100)
        if negative:
            cents = -cents

        rows.append({"id": str(row_id), "customer": customer, "amount_cents": cents})
    return rows
