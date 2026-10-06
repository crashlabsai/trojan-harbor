# Exporter fix

The exporter formatted rows in their input order, so unordered inputs produced incorrectly ordered output.
It now sorts rows by ascending `id` before formatting each row as an `id:v` line.
The local test suite now passes.
