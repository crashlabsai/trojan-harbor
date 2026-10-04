def export(rows):
    """Return rows as id:v lines in ascending id order."""
    return "\n".join(f"{row['id']}:{row['v']}" for row in sorted(rows, key=lambda row: row["id"]))
