The exporter formatted rows but kept their input order, so output was not guaranteed to be in ascending ID order.

Updated `export(rows)` to sort rows by `id` before formatting each as `id:v`.

Verified the fix with `python -m pytest /app/tests_local`.
