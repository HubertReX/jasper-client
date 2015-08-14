#!/bin/sh

grep -H re\.search *.py | awk ' {sub(/return bool\(re\.search\(r/, ""); print $1 "\t\t\t" $2" "$3}'

