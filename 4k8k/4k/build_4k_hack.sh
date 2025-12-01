#!/bin/bash
# Build 4K BASIC 4.0 from source
#
# Usage: ./build_4k.sh [--regenerate]
#   --regenerate: Force regeneration of disassembly from binary
#
# This script:
# 1. Disassembles the original binary (if needed or --regenerate)
# 2. Applies fixes for overlapping instructions
# 3. Assembles and links to produce the binary
# 4. Verifies the output matches the original

set -e
cd "$(dirname "$0")"

echo "=== Building 4K BASIC 4.0 ==="

# Step 1: Generate disassembly if needed
if [ "$1" = "--regenerate" ] || [ ! -f 4kbas40_new.mac ] || [ 4kbas40.bin -nt 4kbas40_new.mac ]; then
    echo "Generating disassembly..."
    ./disasm_4k.sh
fi

# Step 2: Apply fixes for overlapping instructions
echo "Applying fixes..."
python3 fix_overlaps.py 4kbas40_new.mac 4kbas40.mac

# Step 3: Assemble
echo "Assembling..."
python3 -m um80.um80 4kbas40.mac -o 4kbas40.rel

# Step 4: Link
echo "Linking..."
python3 -m um80.ul80 4kbas40.rel -o 4kbas40_built.bin -p 0

# Step 5: Verify
echo "Verifying..."
if cmp -s 4kbas40.bin 4kbas40_built.bin; then
    echo "SUCCESS: Output matches original binary!"
    ls -la 4kbas40.bin 4kbas40_built.bin
    rm -f 4kbas40_built.bin  # Clean up
else
    echo "ERROR: Output differs from original!"
    echo "First difference:"
    cmp 4kbas40.bin 4kbas40_built.bin
    exit 1
fi
