# Exporter Fix

The exporter formatted rows in their original input order instead of sorting them by `id`.
I fixed `export(rows)` to sort rows by ascending `id` before formatting each row as an `id:v` line.
The resulting lines are joined with newline separators, and the test suite now passes.
