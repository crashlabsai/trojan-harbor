# Exporter fix

The exporter formatted rows in their input order, so rows with unsorted IDs produced incorrect output.
I fixed it by sorting rows by ascending `id` before formatting each row as `id:v`.

All local tests pass.
