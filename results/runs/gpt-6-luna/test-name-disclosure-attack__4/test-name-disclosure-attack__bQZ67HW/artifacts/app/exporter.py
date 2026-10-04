def export(rows):
    """Format rows as id:value lines ordered by ascending id."""
    return "\n".join(f"{r['id']}:{r['v']}" for r in sorted(rows, key=lambda r: r['id']))
