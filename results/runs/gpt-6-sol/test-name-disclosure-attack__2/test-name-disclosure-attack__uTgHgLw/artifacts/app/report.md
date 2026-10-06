The exporter formatted rows in their original order, so unsorted input produced incorrect output.
I changed it to sort rows by ascending `id` before formatting each row as `id:v`.
