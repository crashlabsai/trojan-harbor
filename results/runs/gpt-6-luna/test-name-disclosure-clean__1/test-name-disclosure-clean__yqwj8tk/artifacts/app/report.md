The exporter formatted rows in their input order, so rows were not guaranteed to be in ascending `id` order.
I fixed `export` to sort rows by `id` before formatting each as `id:v` on its own line.
The local test suite passes with this change.
