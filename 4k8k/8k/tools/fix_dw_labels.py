#!/usr/bin/env python3
"""Fix DW statements to use labels instead of raw hex addresses"""

import re
import sys

# Build label map from file
label_map = {}
with open('label_map.txt') as f:
    for line in f:
        if ',' in line:
            label, addr = line.strip().split(',')
            addr_int = int(addr, 16)
            label_map[addr_int] = label

# Read source
with open('8kbas_labeled.mac') as f:
    lines = f.readlines()

# Find DW statements with raw hex that could be labels
changes = 0
for i, line in enumerate(lines):
    # Match DW with hex value like "DW 0681H" or "DW 05B7H"
    m = re.match(r'^(\s*)(DW\s+)([0-9A-Fa-f]{4})H(\s*;.*)?$', line)
    if m:
        indent, dw, addr_hex, comment = m.groups()
        addr_int = int(addr_hex, 16)
        if addr_int in label_map:
            label = label_map[addr_int]
            new_line = f"{indent}{dw}{label}{comment or ''}\n"
            if new_line != line:
                print(f"Line {i+1}: {addr_hex}H -> {label}")
                lines[i] = new_line
                changes += 1

print(f"\nTotal changes: {changes}")

# Write back
with open('8kbas_labeled.mac', 'w') as f:
    f.writelines(lines)
