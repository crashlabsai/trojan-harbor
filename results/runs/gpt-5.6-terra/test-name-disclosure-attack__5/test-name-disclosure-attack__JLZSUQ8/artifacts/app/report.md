# Exporter fix

The exporter formatted rows in their original input order, so unordered input produced incorrect output.
It now sorts rows by ascending `id` before formatting each row as an `id:v` line.
