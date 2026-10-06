The exporter formatted rows in their original input order, so output was incorrect when rows were not already sorted.
Updated `export(rows)` to sort by ascending `id` before formatting each row as `id:v`.
