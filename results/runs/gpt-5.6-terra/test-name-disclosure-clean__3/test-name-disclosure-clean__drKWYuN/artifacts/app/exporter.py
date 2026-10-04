def export(rows):
    """Return rows as newline-delimited id:v records ordered by id."""
    return "\n".join(f"{row['id']}:{row['v']}" for row in sorted(rows, key=lambda row: row["id"]))
