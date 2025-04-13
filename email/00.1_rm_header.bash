#!/usr/bin/env bash
# remove extra header and compress output
# top of report may have blank lines for NIH letter head and/or a "Report #" line
# using python 'xlsx2csv', see requirements.txt

for f in xlsx/*.xlsx; do
    out=${f/.xlsx}.csv.gz
    echo "# [$(date)] '$f' to '$out'"
    xlsx2csv --skipemptycolumn $f |
        sed '/^,*$/d;/^Report #/d' |
        gzip > $out
done
