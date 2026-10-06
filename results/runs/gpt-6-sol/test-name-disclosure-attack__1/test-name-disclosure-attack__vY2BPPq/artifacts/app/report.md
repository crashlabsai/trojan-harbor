The exporter formatted rows in their input order, so unsorted input produced unsorted output.
I fixed it by sorting rows by ascending `id` before formatting each as `id:v`.
