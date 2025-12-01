#!/bin/bash
# Build 8K BASIC 4.0 from source
#
# Usage: ./build_8k.sh
#
# This script:
# 1. Assembles the labeled disassembly
# 2. Links to produce the binary
# 3. Verifies the output matches the original

set -e
cd "$(dirname "$0")"

echo "=== Building 8K BASIC 4.0 ==="

# Step 1: Assemble
echo "Assembling..."
um80 8kbas_labeled.mac -o 8kbas_labeled.rel

# Step 2: Link (note: -p 0 for raw binary, not CP/M COM format)
echo "Linking..."
ul80 8kbas_labeled.rel -o 8kbas_built.bin -p 0

# Step 3: Verify
echo "Verifying..."
if cmp -s 8kbas.bin 8kbas_built.bin; then
    echo "SUCCESS: Output matches original binary!"
    ls -la 8kbas.bin 8kbas_built.bin
    rm -f 8kbas_built.bin  # Clean up
else
    echo "ERROR: Output differs from original!"
    echo "First difference:"
    cmp 8kbas.bin 8kbas_built.bin
    exit 1
fi
