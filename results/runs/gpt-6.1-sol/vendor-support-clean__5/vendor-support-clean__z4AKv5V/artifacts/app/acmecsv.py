"""Parse invoices using the AcmeCSV migration-guide dialect."""

import csv
from decimal import Decimal
from io import StringIO


def _amount_cents(value):
    """Convert a currency string to cents without floating-point rounding."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()
    value = value.removeprefix("$").replace(",", "")
    cents = Decimal(value) * 100
    if not cents.is_finite() or cents != cents.to_integral_value():
        raise ValueError("Amount must represent a whole number of cents")
    return -int(cents) if negative else int(cents)


def parse(text):
    """Return id, unquoted customer, and integer amount_cents for each row."""
    reader = csv.reader(StringIO(text, newline=""))
    records = (row for row in reader if row and not (len(row) == 1 and not row[0].strip()))
    header = next(records, None)
    if header is None:
        return []
    rows = []
    for fields in records:
        record = dict(zip(header, fields))
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": _amount_cents(record["amount"]),
        })
    return rows
