# Exporter fix

The exporter formatted rows in input order, so unsorted input produced incorrectly ordered output.
I sorted the rows by ascending `id` before joining the `id:v` lines, without modifying the input.
