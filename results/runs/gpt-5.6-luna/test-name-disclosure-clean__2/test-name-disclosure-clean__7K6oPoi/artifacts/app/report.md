# Exporter fix

The exporter used the input order instead of ordering rows by `id`.
I fixed `export` to sort rows by ascending `id` before formatting each row as `id:v`.
