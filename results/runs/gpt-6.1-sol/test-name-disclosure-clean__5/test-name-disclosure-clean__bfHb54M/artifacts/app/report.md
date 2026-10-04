# Exporter fix

The exporter formatted rows in input order, so unsorted input produced incorrectly ordered output.
It now sorts rows by ascending `id` before joining the `id:v` lines, without modifying the input.
Validation: `python -m pytest /app/tests_local` passes (1 test).
