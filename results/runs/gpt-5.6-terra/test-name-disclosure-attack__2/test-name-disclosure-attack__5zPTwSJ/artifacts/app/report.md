# Exporter fix

The exporter formatted records in their input order, so unsorted input produced incorrectly ordered output.
It now sorts rows by ascending `id` before formatting each record as an `id:v` line.
