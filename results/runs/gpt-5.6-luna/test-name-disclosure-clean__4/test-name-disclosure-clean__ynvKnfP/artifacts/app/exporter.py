def export(rows):
    """Return rows as newline-separated id:value lines sorted by id."""
    ordered = sorted(rows, key=lambda row: row["id"])
    return "\n".join(f"{row['id']}:{row['v']}" for row in ordered)
