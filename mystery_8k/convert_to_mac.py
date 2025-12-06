#!/usr/bin/env python3
"""
Convert AltairBASIC-1975-v2.txt listing to .mac assembly source.
Strips addresses and hex bytes, keeps labels, mnemonics, operands, comments.
"""

import re
import sys


def fix_comment_separator(line: str) -> str:
    """Fix comment separators - ensure ; not : and proper spacing."""
    # Replace : with ; in comment context (after operand, before text)
    # Pattern: tab or spaces, then : followed by text
    line = re.sub(r'(\s):([A-Za-z])', r'\1;\2', line)
    line = re.sub(r'(\s):(\')', r'\1;\2', line)
    # Fix missing ; before comment text (operand followed by spaces and text)
    # This is tricky - look for patterns like "cinb    sget" where sget is a comment
    return line


def convert_line(line: str) -> str:
    """Convert a listing line to assembly source."""
    # Skip page headers
    if line.startswith('===') or 'basIC.LST' in line:
        return None

    # Empty line
    if not line.strip():
        return ''

    # Fix comment separators early
    line = fix_comment_separator(line)

    # Comment-only line (starts with ;)
    if line.strip().startswith(';'):
        return line.strip()

    # Label-only line (word followed by colon, no address)
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*$', line)
    if m:
        return m.group(1) + ':'

    # Label with comment
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(;.*)$', line)
    if m:
        return m.group(1) + ':\t' + m.group(2)

    # EQU line with address prefix
    # Pattern: ADDR VALUE  NAME EQU VALUE (check before generic address pattern)
    m = re.match(r'^[0-9A-F]{4} [0-9A-F]{2,6}\s+(\S+)\s+(EQU|CEQU)\s+(.+)$', line, re.IGNORECASE)
    if m:
        name = m.group(1)
        directive = m.group(2).upper()
        value = m.group(3)
        if directive == 'CEQU':
            directive = 'EQU'  # Fix OCR error
        return name + '\tEQU\t' + value

    # Line with address and inline label: ADDR HEX  LABEL: MNEMONIC
    m = re.match(r'^[0-9A-F]{4} [0-9A-F]{2,6}\s+([A-Za-z_][A-Za-z0-9_]*):\s*(.+)$', line)
    if m:
        label = m.group(1)
        rest = m.group(2)
        return label + ':\t' + rest

    # Line with address: ADDR HEX  MNEMONIC OPERAND ;COMMENT
    m = re.match(r'^[0-9A-F]{4} [0-9A-F]{2,6}\s+(.+)$', line)
    if m:
        rest = m.group(1)
        return '\t' + rest

    # Line with just address and hex (data continuation)
    m = re.match(r'^[0-9A-F]{4} [0-9A-F]{2,6}\s*$', line)
    if m:
        return None  # Skip data-only lines

    # Label on line by itself with trailing content
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.+)$', line)
    if m:
        label = m.group(1)
        rest = m.group(2).strip()
        if rest.startswith(';'):
            return label + ':\t' + rest
        else:
            return label + ':\n\t' + rest

    # Anything else - pass through
    return line


def convert_file(input_path: str, output_path: str):
    """Convert listing file to .mac source."""
    with open(input_path, 'r') as f:
        lines = f.readlines()

    output_lines = []
    for line in lines:
        line = line.rstrip()
        result = convert_line(line)
        if result is not None:
            output_lines.append(result)

    with open(output_path, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')

    print(f"Converted {len(lines)} lines to {len(output_lines)} lines")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    input_file = 'AltairBASIC-1975-v2.txt'
    output_file = 'AltairBASIC-1975.mac'

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    convert_file(input_file, output_file)
