# Exporter fix

The exporter formatted rows in their input order, so unsorted input produced output in the wrong order.
It now sorts rows by ascending `id` before formatting each row as an `id:v` line.
