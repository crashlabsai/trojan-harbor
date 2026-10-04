"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    """Convert an AcmeCSV currency amount to an integer number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    # AcmeCSV uses commas only as thousands separators and an optional leading
    # dollar sign. Decimal avoids the rounding errors inherent in float.
    if value.startswith("$"):
        value = value[1:]
    cents = int(Decimal(value.replace(",", "")) * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dictionaries."""
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for record in reader:
        # Ignore entirely blank physical data rows while retaining CSV fields
        # that legitimately contain embedded newlines.
        if not record or not any(value is not None and value.strip() for value in record.values()):
            continue
        rows.append(
            {
                "id": record["id"],
                "customer": record["customer"],
                "amount_cents": _amount_to_cents(record["amount"]),
            }
        )
    return rows
