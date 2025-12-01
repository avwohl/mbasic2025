#!/usr/bin/env python3
"""Convert consecutive DB pairs to DW statements with labels"""

import re

# Build label map
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

def get_db_value(line):
    """Extract the DB value from a line"""
    m = re.search(r'\bDB\s+([0-9A-Fa-f]+)H', line)
    if m:
        return int(m.group(1), 16)
    return None

def get_address_comment(line):
    """Extract address from comment like '; 0043' or '; 0043:'"""
    m = re.search(r';\s*([0-9A-Fa-f]{4})', line)
    if m:
        return int(m.group(1), 16)
    return None

def get_label(line):
    """Extract label from line if present"""
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line)
    if m:
        return m.group(1)
    return None

changes = []
i = 0
while i < len(lines) - 1:
    line = lines[i]
    addr = get_address_comment(line)
    
    # STMT_DISPATCH table: 0x0043 to 0x0071 (inclusive), pairs of bytes
    if addr is not None and 0x0043 <= addr <= 0x0071 and (addr - 0x0043) % 2 == 0:
        val1 = get_db_value(line)
        next_line = lines[i+1]
        val2 = get_db_value(next_line)
        addr2 = get_address_comment(next_line)
        
        if val1 is not None and val2 is not None and addr2 == addr + 1:
            # This is a pair - convert to DW
            target_addr = val1 + (val2 << 8)  # little-endian
            label = label_map.get(target_addr, f"L{target_addr:04X}")
            
            # Get the label from first line if present
            line_label = get_label(line)
            prefix = f"{line_label}:\t" if line_label else "\t"
            
            new_line = f"{prefix}DW\t{label}\t; {addr:04X}: {val1:02X} {val2:02X}\n"
            changes.append((i, new_line, addr, target_addr, label))
            i += 2
            continue
    
    i += 1

print(f"Found {len(changes)} DB pairs to convert to DW")
for idx, new_line, addr, target, label in changes:
    print(f"  {addr:04X}: -> DW {label} ({target:04X})")

# Apply changes in reverse order
for idx, new_line, addr, target, label in reversed(changes):
    lines[idx] = new_line
    del lines[idx + 1]

# Write back
with open('8kbas_labeled.mac', 'w') as f:
    f.writelines(lines)

print(f"\nApplied {len(changes)} changes")
