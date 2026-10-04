# Exporter fix

The exporter formatted rows in their input order, causing unsorted IDs in the output.
It now sorts rows by ascending `id` before joining them as `id:v` lines.
Using `sorted` leaves the original input unchanged.
