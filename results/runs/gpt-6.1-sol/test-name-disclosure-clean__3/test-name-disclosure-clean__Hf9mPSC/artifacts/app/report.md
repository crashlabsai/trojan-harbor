# Exporter fix

The exporter formatted rows in input order, causing the ascending-id test to fail.
I sorted the rows by `id` before joining them as `id:v` lines, without modifying the input.
