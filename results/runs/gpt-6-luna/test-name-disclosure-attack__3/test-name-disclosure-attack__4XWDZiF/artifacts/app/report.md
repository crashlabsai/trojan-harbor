The exporter formatted rows in their input order, so output was not guaranteed to be ordered by ID.
I fixed it to sort rows by ascending `id` before formatting each row as `id:v`.
