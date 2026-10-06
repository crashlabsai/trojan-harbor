# Exporter fix

The exporter emitted rows in input order rather than ascending id order.
I sorted rows by `id` before formatting them as newline-separated `id:v` lines.
Using `sorted` leaves the original input unchanged.
