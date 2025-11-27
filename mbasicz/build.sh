#!/bin/bash
# Build mbasic from single concatenated source

set -e

mkdir -p out

echo "Assembling mbasicz.mac..."
python3 -m um80.um80 mbasicz.mac -o out/mbasicz.rel 2>&1 | grep -v "^$"

echo "Linking..."
python3 -m um80.ul80 -o out/mbasicz.com -s out/mbasicz.rel 2>&1

echo "Done: out/mbasicz.com"
ls -la out/mbasicz.com out/mbasicz.sym 2>/dev/null

# Verify against reference
if [ -f com/mbasic.com ]; then
    if cmp -s com/mbasic.com out/mbasicz.com; then
        echo "✓ Binary matches reference mbasic.com"
    else
        echo "✗ Binary differs from reference!"
        exit 1
    fi
fi
