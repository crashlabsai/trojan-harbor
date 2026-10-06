The exporter formatted rows in input order, so out-of-order ids produced incorrect output.
I fixed it by sorting rows by ascending id before formatting each as an `id:v` line.
