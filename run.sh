#!/bin/bash
echo 'INFO:'
echo 'grammar: g.txt'
echo 'place the test codes in "tests" directory'
echo 'other files: special_tokens.txt keywords.txt'
for f in `ls tests`
do
    echo
    echo "### Test code: $f ###"
    cp tests/"$f" code.c
    python3 parser.py
done

