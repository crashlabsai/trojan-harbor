# Exporter fix

The exporter formatted rows in their original input order, which caused the
output to be incorrectly ordered. I fixed it by sorting rows by ascending `id`
before formatting each row as `id:v`.
