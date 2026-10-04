# Exporter fix

The exporter formatted rows in input order, so unsorted input produced incorrectly ordered output.
It now sorts rows by ascending `id` before joining their `id:v` lines.
