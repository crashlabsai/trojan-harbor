# Exporter fix

The exporter formatted rows in their original input order, so unordered inputs produced incorrect output.
It now sorts rows by ascending `id` before rendering each row as an `id:v` line.
