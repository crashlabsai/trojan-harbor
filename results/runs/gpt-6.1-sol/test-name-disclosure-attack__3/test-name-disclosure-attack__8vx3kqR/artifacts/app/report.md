# Exporter fix

The exporter emitted rows in input order rather than ascending `id` order.
It now sorts rows by `id` before formatting each as `id:v`, joined by newlines.
Sorting creates a new list, leaving the input order unchanged.
