def export(rows):
    """Return rows as id:value lines ordered by ascending id."""
    ordered_rows = sorted(rows, key=lambda row: row["id"])
    return "\n".join(f"{row['id']}:{row['v']}" for row in ordered_rows)
