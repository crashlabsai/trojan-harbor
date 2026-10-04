# Exporter fix

The exporter formatted rows in input order instead of ascending `id` order.
I added sorting by `id` before formatting each row as `id:v`, joined by newlines.
Using `sorted()` leaves the input rows unchanged.
