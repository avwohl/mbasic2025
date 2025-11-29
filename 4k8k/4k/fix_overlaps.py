#!/usr/bin/env python3
"""
Post-process the disassembly to fix:
1. Overlapping instruction regions
2. DC (high-bit terminated string) directives -> DB bytes

These regions use a clever 8080 trick where a 3-byte instruction (like LXI)
has a 1-byte instruction (like MVI) embedded starting at byte 2, creating
two entry points into the same bytes.

DC directives need conversion because um80 doesn't support high-bit termination.
"""

import re
import sys

# Overlapping regions that need special handling:
# Each tuple: (start_addr, end_addr, replacement_lines)
OVERLAP_FIXES = [
    # OutOfMemory/SyntaxError/DivByZero at 01D3-01DA
    # 01D3: 1E 0C = MVI E,0C (OutOfMemory: error code OM)
    # 01D5: 01    = LXI B,... (skip next 2 bytes when falling through)
    # 01D6: 1E 02 = MVI E,02 (SyntaxError: error code SN)
    # 01D8: 01    = LXI B,... (skip next 2 bytes when falling through)
    # 01D9: 1E 14 = MVI E,14 (DivByZero: error code /0)
    (0x01D3, 0x01DA, """\
OutOfMemory:\t\tMVI\tE,0CH\t; 01D3: Error code 0C (OM)
\t\t\tDB\t01H\t\t; 01D5: LXI B (swallows next 2 bytes)
SyntaxError:\t\tDB\t1EH\t\t; 01D6: MVI E (when entered as SyntaxError)
\t\t\tDB\t02H\t\t; 01D7: Error code 02 (SN)
\t\t\tDB\t01H\t\t; 01D8: LXI B (swallows next 2 bytes)
D01D9:
DivByZero:\t\tDB\t1EH\t\t; 01D9: MVI E (when entered as DivByZero)
\t\t\tDB\t14H\t\t; 01DA: Error code 14 (/0)"""),

    # Stop/Main area at 01FC-01FE
    # 01FC: 01 C0 C1 = LXI B,C1C0 (fall through)
    # 01FD: C0      = RNZ (Stop: return if syntax error)
    # 01FE: C1      = POP B (Pop return address)
    (0x01FC, 0x01FE, """\
\t\t\tDB\t01H\t\t; 01FC: LXI B (swallows next 2 bytes)
Stop:\t\t\tDB\t0C0H\t\t; 01FD: RNZ (return if args present)
\t\t\tDB\t0C1H\t\t; 01FE: POP B (discard return address)"""),

    # FindNextStatement/Rem at 0503-0506
    # 0503: 01 3A 0E = LXI B,0E3A (C=':' for FindNextStatement)
    # 0505: 0E 00    = MVI C,00 (C=0 for Rem)
    (0x0503, 0x0506, """\
FindNextStatement:\tDB\t01H\t\t; 0503: LXI B (swallows next 2 bytes)
\t\t\tDB\t3AH\t\t; 0504: ':' for statement separator
Rem:\t\t\tDB\t0EH\t\t; 0505: MVI C (when entered as Rem)
\t\t\tDB\t00H\t\t; 0506: Null terminator"""),
]

def convert_dc_to_db(line):
    """Convert a DC directive to DB bytes with high-bit termination.

    DC 'ABC' -> DB 41H,42H,C3H  (last char | 0x80)
    """
    # Match DC directive: label:\t\tDC\t'string'\t; comment
    m = re.match(r"^(\S*:)?\s*DC\s+'([^']+)'(.*)$", line)
    if not m:
        return line  # Not a DC line

    label = m.group(1) or ''
    string = m.group(2)
    comment = m.group(3)

    # Convert string to hex bytes, last char with high bit set
    hex_bytes = []
    for i, c in enumerate(string):
        val = ord(c)
        if i == len(string) - 1:
            val |= 0x80  # Set high bit on last char
        hex_bytes.append(f'{val:02X}H')

    # Format as DB line
    hex_str = ','.join(hex_bytes)
    if label:
        return f"{label}\tDB\t{hex_str}{comment}\n"
    else:
        return f"\t\tDB\t{hex_str}{comment}\n"


def fix_dc_in(line):
    """Fix the DC 'IN' entry which should be plain DB since it's followed by 80H terminator."""
    if "DC\t'IN'" in line and '00C9' in line:
        return line.replace("DC\t'IN'", "DB\t'I','N'")
    return line


def fix_overlaps(input_file, output_file):
    """Read the .mac file and fix overlapping instruction regions."""

    with open(input_file, 'r') as f:
        lines = f.readlines()

    output_lines = []
    skip_until = None

    for line in lines:
        # Check if this line is in a skip region
        if skip_until is not None:
            # Look for address in comment
            m = re.search(r';\s*([0-9A-Fa-f]{4}):', line)
            if m:
                addr = int(m.group(1), 16)
                if addr <= skip_until:
                    continue  # Skip this line
                else:
                    skip_until = None  # Done skipping

        # Check if this line starts an overlap region
        for start_addr, end_addr, replacement in OVERLAP_FIXES:
            m = re.search(r';\s*([0-9A-Fa-f]{4}):', line)
            if m:
                addr = int(m.group(1), 16)
                if addr == start_addr:
                    # Insert replacement
                    output_lines.append(replacement + '\n')
                    skip_until = end_addr
                    break
        else:
            # Not in an overlap region, keep the line
            if skip_until is None:
                line = fix_dc_in(line)
                output_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(output_lines)

    print(f"Processed {len(lines)} lines, output {len(output_lines)} lines")
    print(f"Fixed {len(OVERLAP_FIXES)} overlapping instruction regions")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.mac output.mac")
        sys.exit(1)
    fix_overlaps(sys.argv[1], sys.argv[2])
