# Exporter fix

The exporter formatted rows in their input order instead of ascending `id` order.
I fixed it by sorting rows by `id` before formatting each row as an `id:v` line.
