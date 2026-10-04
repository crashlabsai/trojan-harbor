The exporter formatted rows in their original input order, so output was incorrect when IDs were unsorted.
It now sorts rows by ascending `id` before formatting each row as `id:v`.
