"""Offline unit conversion client."""


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Return *value* converted from ``from_unit`` to ``to_unit``."""
    factors = {
        "m": 1.0,
        "cm": 0.01,
        "mm": 0.001,
        "km": 1000.0,
    }
    return value * factors[from_unit] / factors[to_unit]
