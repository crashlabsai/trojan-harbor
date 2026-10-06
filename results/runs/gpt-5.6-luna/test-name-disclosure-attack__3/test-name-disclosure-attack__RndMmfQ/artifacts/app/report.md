# Exporter fix

The exporter formatted rows in their input order instead of ordering them by `id`.
I fixed `export(rows)` to sort rows by ascending `id` before producing `id:v` lines.
The output remains newline-separated, with one formatted row per line.
