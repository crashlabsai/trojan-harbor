def export(rows):
    """Format rows as id:value lines sorted by ascending id."""
    return "\n".join(
        f"{row['id']}:{row['v']}" for row in sorted(rows, key=lambda row: row['id'])
    )
