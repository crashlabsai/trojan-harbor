# Exporter fix

The exporter formatted rows in their input order, rather than ordering them by `id`.
It now sorts rows by ascending `id` before producing the `id:v` lines.
