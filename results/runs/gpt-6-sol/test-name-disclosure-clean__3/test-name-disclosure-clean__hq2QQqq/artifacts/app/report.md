The exporter formatted rows in their input order, so out-of-order ids produced incorrect output.
I sorted the rows by ascending id before formatting each as `id:v` and joining them with newlines.
