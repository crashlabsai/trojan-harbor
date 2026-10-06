"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    """Convert an AcmeCSV currency value to an exact integer cent amount."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    # AcmeCSV uses a leading dollar sign and commas only as thousands separators.
    value = value.removeprefix("$").replace(",", "")
    cents = Decimal(value) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"amount has fractions of a cent: {value!r}")

    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into a list of normalized row dictionaries."""
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = []
    for record in reader:
        # Constructing the result explicitly guarantees the required shape.
        rows.append(
            {
                "id": record["id"],
                "customer": record["customer"],
                "amount_cents": _amount_to_cents(record["amount"]),
            }
        )
    return rows
