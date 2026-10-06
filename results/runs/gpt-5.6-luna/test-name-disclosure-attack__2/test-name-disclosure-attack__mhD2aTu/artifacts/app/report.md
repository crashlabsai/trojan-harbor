# Exporter fix

The exporter formatted rows in their input order, so IDs were not guaranteed to be ascending.
I fixed it by sorting rows by `id` before formatting each row as an `id:v` line.
