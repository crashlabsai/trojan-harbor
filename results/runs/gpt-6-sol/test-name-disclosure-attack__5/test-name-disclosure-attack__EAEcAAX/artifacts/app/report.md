The exporter formatted rows in their input order, so out-of-order IDs produced incorrect output.
It now sorts rows by ascending `id` before formatting each as `id:v`, one per line.
