def export(rows):
    """Return newline-separated id:v rows ordered by ascending id."""
    return "\n".join(
        f"{r['id']}:{r['v']}" for r in sorted(rows, key=lambda r: r['id'])
    )
