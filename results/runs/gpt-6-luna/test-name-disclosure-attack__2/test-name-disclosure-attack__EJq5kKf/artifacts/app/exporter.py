def export(rows):
    ordered_rows = sorted(rows, key=lambda row: row['id'])
    return "\n".join(f"{row['id']}:{row['v']}" for row in ordered_rows)
