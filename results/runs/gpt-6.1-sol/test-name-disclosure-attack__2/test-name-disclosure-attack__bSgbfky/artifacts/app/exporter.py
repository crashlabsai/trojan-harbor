def export(rows):
    """Format rows as id:v lines in ascending id order."""
    return "\n".join(f"{r['id']}:{r['v']}" for r in sorted(rows, key=lambda r: r['id']))
