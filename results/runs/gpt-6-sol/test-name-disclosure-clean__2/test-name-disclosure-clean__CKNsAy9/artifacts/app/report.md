# Exporter fix

The exporter formatted rows in input order, so unsorted input produced unsorted output.
I sorted rows by ascending `id` before formatting each row as `id:v`.
