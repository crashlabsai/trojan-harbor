"""AcmeCSV invoice parser."""

import csv
from decimal import Decimal
from io import StringIO


def _amount_cents(value):
    """Convert an AcmeCSV currency field to an integral number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    # Thousands separators are valid only inside a CSV-quoted field; csv has
    # already recovered the complete field before this normalization happens.
    if value.startswith("$"):
        value = value[1:]
    cents = int(Decimal(value.replace(",", "")) * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into AcmeCSV invoice row dictionaries."""
    reader = csv.reader(StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return []

    columns = {name: index for index, name in enumerate(header)}
    rows = []
    for fields in reader:
        if not fields or not any(fields):
            continue
        rows.append({
            "id": fields[columns["id"]],
            "customer": fields[columns["customer"]],
            "amount_cents": _amount_cents(fields[columns["amount"]]),
        })
    return rows
