# Exporter fix

`export()` previously preserved the input row order, so unsorted rows produced
incorrect output. It now sorts rows by ascending `id` before formatting each as
an `id:v` line.
