#!/usr/bin/env python3
"""
Extract symbols (labels and EQU values) from the listing file.
Creates a table of expected symbol names and addresses.
"""

import re
import sys


def extract_symbols(input_path: str, output_path: str):
    """Extract symbols from listing file."""
    with open(input_path, 'r') as f:
        lines = f.readlines()

    symbols = {}

    for line in lines:
        line = line.rstrip()

        # Skip headers
        if line.startswith('===') or 'basIC.LST' in line or not line.strip():
            continue

        # Pattern 1: Label on its own line (LABELNAME:)
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*$', line)
        if m:
            # The address will be on the next line with code
            # For now, skip standalone labels
            continue

        # Pattern 2: Label with code on same line (ADDR HEX... LABEL: or just LABEL:)
        # Look for label at start followed by address line

        # Pattern 3: EQU definition
        # ADDR VALUE  NAME EQU VALUE
        m = re.match(r'^[0-9A-F]{4}\s+[0-9A-F]{2,4}\s+(\S+)\s+EQU\s+(\S+)', line, re.IGNORECASE)
        if m:
            name = m.group(1)
            value = m.group(2)
            # Try to parse the value
            if value.upper().endswith('H'):
                try:
                    addr = int(value[:-1], 16)
                    symbols[name.upper()] = addr
                except ValueError:
                    pass
            elif value.isdigit():
                symbols[name.upper()] = int(value)
            continue

        # Pattern 4: Code line with label
        # ADDR HEX  MNEMONIC  or  LABEL:
        # First, check for address at start
        m = re.match(r'^([0-9A-F]{4})\s+[0-9A-F]{2}', line)
        if m:
            addr = int(m.group(1), 16)
            # Check if there's a label on this line or the previous line referenced this address
            # For now, we need to track labels that precede code
            continue

        # Pattern 5: Label line that precedes code
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):?\s*(;.*)?$', line)
        if m:
            label = m.group(1)
            # Need to find the next line with an address
            continue

    # Second pass: find labels and their addresses
    prev_label = None
    for i, line in enumerate(lines):
        line = line.rstrip()

        # Skip headers
        if line.startswith('===') or 'basIC.LST' in line or not line.strip():
            continue

        # Check for label-only line
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):?\s*(;.*)?$', line)
        if m and not re.match(r'^[0-9A-F]{4}\s', line):
            prev_label = m.group(1)
            continue

        # Check for address line
        m = re.match(r'^([0-9A-F]{4})\s+[0-9A-F]{2}', line)
        if m:
            addr = int(m.group(1), 16)
            if prev_label:
                symbols[prev_label.upper()] = addr
                prev_label = None

            # Also check for inline label (ADDR HEX LABEL: MNEMONIC)
            # This is rare in this format
            continue

        # Check for EQU on line without standard format
        if 'EQU' in line.upper():
            m = re.match(r'^[0-9A-F]{4}\s+[0-9A-F]{2,4}\s+(\S+)\s+EQU\s+([0-9A-Fa-f]+)H?\b', line, re.IGNORECASE)
            if m:
                name = m.group(1)
                value_str = m.group(2)
                try:
                    addr = int(value_str, 16)
                    symbols[name.upper()] = addr
                except ValueError:
                    pass

        prev_label = None

    # Sort by address
    sorted_symbols = sorted(symbols.items(), key=lambda x: x[1])

    # Write output
    with open(output_path, 'w') as f:
        f.write("; Expected symbols from listing\n")
        f.write("; NAME = ADDRESS\n")
        f.write(";\n")
        for name, addr in sorted_symbols:
            f.write(f"{name}\tEQU\t{addr:04X}H\n")

    print(f"Extracted {len(symbols)} symbols")
    print(f"Output: {output_path}")

    return symbols


if __name__ == '__main__':
    input_file = 'AltairBASIC-1975-v2.txt'
    output_file = 'expected_symbols.txt'

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    extract_symbols(input_file, output_file)
