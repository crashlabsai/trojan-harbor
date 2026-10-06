The exporter formatted rows in their input order, so output was not guaranteed to be ordered by ID.
It now sorts rows by ascending `id` before formatting each row as `id:v`.
The local pytest suite passes with the fix.
