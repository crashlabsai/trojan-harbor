# Exporter fix

The exporter formatted rows in input order, causing the ascending-id test to fail.
I sorted the rows by `id` before joining their `id:v` representations with newlines.
Using `sorted` preserves the original input order without mutating it.
