# Exporter fix

The exporter formatted rows in their original order, so unsorted input produced incorrectly ordered output.
I sorted the rows by ascending `id` before formatting them as `id:v` lines.
