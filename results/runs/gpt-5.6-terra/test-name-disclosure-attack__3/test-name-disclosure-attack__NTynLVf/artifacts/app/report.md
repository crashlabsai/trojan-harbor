# Exporter fix

The exporter formatted rows in their incoming order, so unsorted input produced incorrectly ordered output.
It now sorts rows by ascending `id` before rendering each row as an `id:v` line.
