#!/usr/bin/env python3
"""
Convert JP instructions to JR where possible in Z80 assembly,
using the assembler listing file for accurate addresses.
"""

import re
import sys

def parse_listing(prn_file):
    """Parse the listing file to extract addresses and labels."""
    labels = {}
    jumps = []

    with open(prn_file, 'r') as f:
        for line in f:
            # Format: "linenum  addr  bytes     source"
            # e.g.:  " 1945  0CBF  C2 C9 0C     	JP NZ,stksrc"

            # Extract line number and address
            match = re.match(r'\s*(\d+)\s+([0-9A-Fa-f]+)\s+([0-9A-Fa-f ]+)\s+(.*)$', line)
            if not match:
                continue

            line_num = int(match.group(1))
            addr = int(match.group(2), 16)
            bytecode = match.group(3).strip()
            source = match.group(4)

            # Look for labels (word followed by colon)
            label_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', source)
            if label_match:
                label = label_match.group(1)
                labels[label] = addr

            # Look for JP instructions
            # JP opcodes: C3=JP, C2=JP NZ, CA=JP Z, D2=JP NC, DA=JP C
            # Also: E2=JP PO, EA=JP PE, F2=JP P, FA=JP M (can't be JR)
            if bytecode.startswith('C3 ') or bytecode.startswith('C2 ') or \
               bytecode.startswith('CA ') or bytecode.startswith('D2 ') or \
               bytecode.startswith('DA '):
                # Extract target from source
                jp_match = re.search(r'JP\s+(Z,|NZ,|C,|NC,)?([A-Za-z_][A-Za-z0-9_]*)', source)
                if jp_match:
                    condition = jp_match.group(1) or ''
                    target = jp_match.group(2)
                    jumps.append({
                        'line_num': line_num,
                        'addr': addr,
                        'condition': condition.rstrip(',') if condition else '',
                        'target': target,
                        'source': source
                    })

    return labels, jumps


def find_convertible(labels, jumps):
    """Find jumps that can be converted to JR."""
    convertible = []

    for jump in jumps:
        target = jump['target']
        if target not in labels:
            continue

        target_addr = labels[target]
        # JR offset is from address after the JR instruction (JR is 2 bytes)
        jump_addr = jump['addr']
        jr_end_addr = jump_addr + 2  # JR is 2 bytes

        displacement = target_addr - jr_end_addr

        # JR range is -128 to +127
        if -128 <= displacement <= 127:
            convertible.append({
                **jump,
                'target_addr': target_addr,
                'displacement': displacement
            })

    return convertible


def apply_conversions(source_file, convertible):
    """Apply the conversions to the source file."""
    # Build line number to conversion map
    convert_lines = {c['line_num']: c for c in convertible}

    with open(source_file, 'r') as f:
        lines = f.readlines()

    new_lines = []
    converted = 0

    for i, line in enumerate(lines, 1):
        if i in convert_lines:
            c = convert_lines[i]
            cond = c['condition']
            target = c['target']

            # Replace JP with JR in the line
            if cond:
                # JP Z,label -> JR Z,label
                new_line = re.sub(
                    r'\bJP\s+' + re.escape(cond) + r',\s*' + re.escape(target) + r'\b',
                    f'JR {cond},{target}',
                    line
                )
            else:
                # JP label -> JR label
                new_line = re.sub(
                    r'\bJP\s+' + re.escape(target) + r'\b',
                    f'JR {target}',
                    line
                )

            if new_line != line:
                converted += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    return new_lines, converted


def main():
    prn_file = sys.argv[1] if len(sys.argv) > 1 else 'out/mbasicz.prn'
    source_file = sys.argv[2] if len(sys.argv) > 2 else 'mbasicz.mac'

    print(f"Parsing listing file: {prn_file}")
    labels, jumps = parse_listing(prn_file)
    print(f"Found {len(labels)} labels and {len(jumps)} convertible JP instructions")

    convertible = find_convertible(labels, jumps)
    print(f"Found {len(convertible)} jumps that can be converted to JR")

    # Show some examples
    print("\nExamples:")
    for c in convertible[:10]:
        cond = c['condition']
        if cond:
            new_inst = f"JR {cond},{c['target']}"
        else:
            new_inst = f"JR {c['target']}"
        print(f"  Line {c['line_num']}: JP -> {new_inst} (disp: {c['displacement']:+d})")

    if len(convertible) > 10:
        print(f"  ... and {len(convertible) - 10} more")

    # Apply conversions
    print(f"\nApplying conversions to {source_file}...")
    new_lines, converted = apply_conversions(source_file, convertible)

    # Write back
    with open(source_file, 'w') as f:
        f.writelines(new_lines)

    print(f"Converted {converted} JP instructions to JR")


if __name__ == '__main__':
    main()
