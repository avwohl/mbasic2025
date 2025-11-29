#!/usr/bin/env python3
"""
Convert DEC B / JR NZ,label sequences to DJNZ label.
DJNZ has same range as JR (-128 to +127).
"""

import re
import sys


def find_and_convert_djnz(source_file):
    """Find DEC B / JR NZ, patterns and convert to DJNZ."""
    with open(source_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    converted = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Check for DEC B (with optional comment)
        dec_match = re.match(r'^(\s*)(DEC B\s*(;.*)?)\s*$', stripped, re.IGNORECASE)

        if dec_match and i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()
            # Check if next line is JR NZ,label
            jr_match = re.match(r'^(\s*)JR NZ,([A-Za-z_][A-Za-z0-9_]*)(\s*;.*)?\s*$', next_line, re.IGNORECASE)

            if jr_match:
                indent = jr_match.group(1)
                label = jr_match.group(2)
                comment = jr_match.group(3) or ''
                orig_comment = dec_match.group(3) or ''

                # Combine comments if both have them
                if orig_comment and comment:
                    final_comment = orig_comment  # Keep first comment
                elif orig_comment:
                    final_comment = orig_comment
                elif comment:
                    final_comment = comment
                else:
                    final_comment = ''

                new_line = f"{indent}DJNZ {label}{final_comment}\n"
                new_lines.append(new_line)
                converted += 1
                i += 2  # Skip both lines
                continue

        # Also check for label: DEC B
        label_dec_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*:)\s*(DEC B\s*(;.*)?)\s*$', stripped, re.IGNORECASE)
        if label_dec_match and i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()
            jr_match = re.match(r'^(\s*)JR NZ,([A-Za-z_][A-Za-z0-9_]*)(\s*;.*)?\s*$', next_line, re.IGNORECASE)

            if jr_match:
                label_prefix = label_dec_match.group(1)
                indent = jr_match.group(1)
                target = jr_match.group(2)
                comment = jr_match.group(3) or ''
                orig_comment = label_dec_match.group(3) or ''

                if orig_comment and comment:
                    final_comment = orig_comment
                elif orig_comment:
                    final_comment = orig_comment
                elif comment:
                    final_comment = comment
                else:
                    final_comment = ''

                new_line = f"{label_prefix}\tDJNZ {target}{final_comment}\n"
                new_lines.append(new_line)
                converted += 1
                i += 2
                continue

        new_lines.append(line)
        i += 1

    return new_lines, converted


def main():
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'mbasicz.mac'

    print(f"Processing {source_file}...")
    new_lines, converted = find_and_convert_djnz(source_file)

    if converted > 0:
        with open(source_file, 'w') as f:
            f.writelines(new_lines)
        print(f"Converted {converted} DEC B / JR NZ patterns to DJNZ")
    else:
        print("No patterns found to convert")


if __name__ == '__main__':
    main()
