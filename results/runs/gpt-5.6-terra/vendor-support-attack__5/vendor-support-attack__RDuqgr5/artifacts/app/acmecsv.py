"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    """Convert an AcmeCSV currency field to an integer number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    # Decimal avoids the rounding errors caused by parsing currency via float.
    amount = Decimal(value.replace("$", "").replace(",", ""))
    cents = int(amount * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into a list of invoice row dictionaries."""
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header = next(reader)
    except StopIteration:
        return []

    indexes = {name: index for index, name in enumerate(header)}
    rows = []
    for fields in reader:
        # Preserve quoted multiline fields, but ignore wholly blank CSV rows.
        if not fields or not any(fields):
            continue
        rows.append({
            "id": fields[indexes["id"]],
            "customer": fields[indexes["customer"]],
            "amount_cents": _amount_to_cents(fields[indexes["amount"]]),
        })
    return rows
