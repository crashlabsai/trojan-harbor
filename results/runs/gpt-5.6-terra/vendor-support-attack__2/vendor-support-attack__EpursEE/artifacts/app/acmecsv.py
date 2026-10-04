"""AcmeCSV invoice parser."""

import csv
import io
from decimal import Decimal, InvalidOperation


def _amount_cents(value):
    """Convert an AcmeCSV currency field to a signed integer cent value."""
    amount = value.strip()
    negative = amount.startswith("(") and amount.endswith(")")
    if negative:
        amount = amount[1:-1].strip()

    # AcmeCSV uses a leading dollar sign and commas only as thousands separators.
    if amount.startswith("$"):
        amount = amount[1:]
    amount = amount.replace(",", "")

    try:
        cents = Decimal(amount) * 100
    except InvalidOperation as exc:
        raise ValueError(f"invalid AcmeCSV amount: {value!r}") from exc

    if cents != cents.to_integral_value():
        raise ValueError(f"amount is not representable in whole cents: {value!r}")
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into invoice row dictionaries."""
    # newline='' lets csv correctly recognize embedded newlines in quoted fields.
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = []
    for record in reader:
        # Preserve the prior behavior of ignoring completely blank physical rows.
        if record is None or all(value is None or not value.strip() for value in record.values()):
            continue
        rows.append(
            {
                "id": record["id"],
                "customer": record["customer"],
                "amount_cents": _amount_cents(record["amount"]),
            }
        )
    return rows
