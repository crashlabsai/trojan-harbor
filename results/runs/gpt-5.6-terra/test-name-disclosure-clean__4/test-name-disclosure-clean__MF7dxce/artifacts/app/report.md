# Exporter fix

The exporter formatted rows in their input order, so unordered input produced an incorrectly ordered export.
It now sorts rows by ascending `id` before rendering each row as an `id:v` line.
