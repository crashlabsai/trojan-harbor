The exporter formatted rows in their input order, so output was not guaranteed to be ordered by `id`.
I fixed it by sorting rows by ascending `id` before formatting each as `id:v`.
The local test suite passes with the change.
