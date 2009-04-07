#!/bin/bash
export PYTHONPATH="$PYTHONPATH${PYTHONPATH+:}$PWD"
if [ -f "tests.py" ]; then
    echo "unittests: tests.py"
    python tests.py || exit
fi
for F in $(find . -type f -name '*.py' ! -size 0); do
    if grep -q "doctest.testmod()" "$F"; then
        echo "doctest: $F"
        python "$F" || exit
    fi
done
