# Exporter fix

The exporter formatted rows in their incoming order, so output was incorrect when IDs were unsorted.
It now sorts rows by ascending `id` before producing newline-delimited `id:v` records.
