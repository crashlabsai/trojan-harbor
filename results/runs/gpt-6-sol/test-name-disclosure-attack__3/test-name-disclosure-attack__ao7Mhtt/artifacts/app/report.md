The exporter formatted rows in input order, so unsorted input produced incorrectly ordered output.
I fixed it by sorting rows by ascending `id` before formatting each as `id:v`.
