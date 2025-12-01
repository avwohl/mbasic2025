#!/usr/bin/env python3
"""
Normalize 8K BASIC assembly to Intel standard format:
- Lowercase opcodes and register names
- Use short register pair names (H not HL, D not DE, B not BC)
- Use tabs for indentation
- Lowercase all-uppercase labels
"""

import re

# Register pair mappings (long to short form)
REG_PAIRS = {
    'HL': 'h',
    'DE': 'd',
    'BC': 'b',
    'SP': 'sp',
    'PSW': 'psw',
}

# Single registers (just lowercase)
SINGLE_REGS = {'A', 'B', 'C', 'D', 'E', 'H', 'L', 'M'}

# Opcodes that use register pairs
PAIR_OPCODES = {
    'DAD', 'DCX', 'INX', 'PUSH', 'POP', 'LXI', 'LDAX', 'STAX'
}

# All 8080 opcodes (only real CPU instructions, not macros/directives)
ALL_OPCODES = {
    'MOV', 'MVI', 'LDA', 'STA', 'LHLD', 'SHLD', 'LXI', 'LDAX', 'STAX',
    'XCHG', 'XTHL', 'SPHL', 'PCHL', 'PUSH', 'POP',
    'ADD', 'ADC', 'ADI', 'ACI', 'SUB', 'SBB', 'SUI', 'SBI',
    'ANA', 'ANI', 'ORA', 'ORI', 'XRA', 'XRI', 'CMP', 'CPI',
    'INR', 'DCR', 'INX', 'DCX', 'DAD', 'DAA',
    'RLC', 'RRC', 'RAL', 'RAR', 'CMA', 'CMC', 'STC',
    'JMP', 'JZ', 'JNZ', 'JC', 'JNC', 'JP', 'JM', 'JPE', 'JPO',
    'CALL', 'CZ', 'CNZ', 'CC', 'CNC', 'CP', 'CM', 'CPE', 'CPO',
    'RET', 'RZ', 'RNZ', 'RC', 'RNC', 'RP', 'RM', 'RPE', 'RPO',
    'RST', 'IN', 'OUT', 'NOP', 'HLT', 'DI', 'EI',
}

# Pseudo-ops to lowercase but not normalize operands
PSEUDO_OPS = {'DB', 'DW', 'DS', 'EQU', 'ORG', 'END'}

def is_all_upper_label(label):
    """Check if label is all uppercase (with underscores/digits allowed)"""
    # Remove underscores and digits, check if rest is all uppercase letters
    letters = re.sub(r'[0-9_]', '', label)
    return len(letters) > 0 and letters.isupper() and not label.startswith('L') or \
           (label.startswith('L') and len(label) > 5)  # L0000 style labels stay as-is

def normalize_operand(opcode, operand):
    """Normalize operand based on opcode type"""
    opcode_upper = opcode.upper()

    # Handle register pairs for pair opcodes
    if opcode_upper in PAIR_OPCODES:
        # LXI has format: LXI rp,data
        if ',' in operand:
            parts = operand.split(',', 1)
            reg = parts[0].strip().upper()
            rest = parts[1].strip()
            if reg in REG_PAIRS:
                return REG_PAIRS[reg] + ',' + rest
            elif reg in SINGLE_REGS:
                return reg.lower() + ',' + rest
            return operand
        else:
            # Just register pair
            reg = operand.strip().upper()
            if reg in REG_PAIRS:
                return REG_PAIRS[reg]
            elif reg in SINGLE_REGS:
                return reg.lower()
            return operand

    # Handle MOV, MVI which use single registers
    if opcode_upper in ('MOV', 'MVI', 'ADD', 'ADC', 'SUB', 'SBB',
                        'ANA', 'ORA', 'XRA', 'CMP', 'INR', 'DCR'):
        parts = operand.split(',')
        result = []
        for part in parts:
            part = part.strip()
            if part.upper() in SINGLE_REGS:
                result.append(part.lower())
            else:
                result.append(part)
        return ','.join(result)

    return operand

def normalize_line(line):
    """Normalize a single line of assembly"""
    # Preserve lines that are pure comments
    stripped = line.lstrip()
    if stripped.startswith(';'):
        return line

    # Preserve empty lines
    if not stripped:
        return line

    # Split into code and comment
    comment = ''
    code = line
    if ';' in line:
        # Find the semicolon (but not in quoted strings)
        idx = line.index(';')
        code = line[:idx]
        comment = line[idx:]

    # Check for label
    label = ''
    label_name = ''
    rest = code
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):(.*)', code)
    if m:
        label_name = m.group(1)
        label = label_name + ':'
        rest = m.group(2)

    # Parse instruction
    rest_stripped = rest.strip()
    if not rest_stripped:
        # Label-only line or empty
        result = label + rest
        if comment:
            result = result.rstrip() + comment
        return result.rstrip() + '\n' if result.strip() else line

    # Split opcode and operands
    parts = rest_stripped.split(None, 1)
    opcode = parts[0]
    operand = parts[1] if len(parts) > 1 else ''

    opcode_upper = opcode.upper()

    # Check if it's a real opcode
    if opcode_upper in ALL_OPCODES:
        # Lowercase opcode
        new_opcode = opcode.lower()

        # Normalize operand
        if operand:
            new_operand = normalize_operand(opcode, operand)
        else:
            new_operand = ''

        # Reconstruct line: tab indent, space between opcode and operand
        if label:
            # Use tab if it goes to column 8 (label < 8 chars), else space
            if len(label) < 8:
                sep = '\t'
            else:
                sep = ' '
            if new_operand:
                new_code = f"{label}{sep}{new_opcode} {new_operand}"
            else:
                new_code = f"{label}{sep}{new_opcode}"
        else:
            # Tab for indentation, space between opcode and operand
            if new_operand:
                new_code = f"\t{new_opcode} {new_operand}"
            else:
                new_code = f"\t{new_opcode}"

        # Add comment - use tabs to align
        if comment:
            # Calculate visual width (tabs = 8 spaces)
            visual_len = 0
            for c in new_code:
                if c == '\t':
                    visual_len = (visual_len // 8 + 1) * 8
                else:
                    visual_len += 1
            # Add tabs to reach column 40
            while visual_len < 40:
                new_code += '\t'
                visual_len = (visual_len // 8 + 1) * 8
            new_code += comment.rstrip()

        return new_code + '\n'

    elif opcode_upper in PSEUDO_OPS:
        # Pseudo-ops: lowercase opcode but preserve operand
        new_opcode = opcode.lower()

        # Reconstruct line: tab indent, space between opcode and operand
        if label:
            # Use tab if it goes to column 8 (label < 8 chars), else space
            if len(label) < 8:
                sep = '\t'
            else:
                sep = ' '
            if operand:
                new_code = f"{label}{sep}{new_opcode} {operand}"
            else:
                new_code = f"{label}{sep}{new_opcode}"
        else:
            if operand:
                new_code = f"\t{new_opcode} {operand}"
            else:
                new_code = f"\t{new_opcode}"

        if comment:
            # Use tabs to align comment at column 40 (5 tabs from start)
            visual_len = 0
            for c in new_code:
                if c == '\t':
                    visual_len = (visual_len // 8 + 1) * 8
                else:
                    visual_len += 1
            while visual_len < 40:
                new_code += '\t'
                visual_len = (visual_len // 8 + 1) * 8
            new_code += comment.rstrip()

        return new_code + '\n'

    else:
        # Not an opcode (macro, directive, RDC, etc.) - preserve as-is
        # but still align comment if present using tabs
        if comment:
            code_part = code.rstrip()
            visual_len = 0
            for c in code_part:
                if c == '\t':
                    visual_len = (visual_len // 8 + 1) * 8
                else:
                    visual_len += 1
            while visual_len < 40:
                code_part += '\t'
                visual_len = (visual_len // 8 + 1) * 8
            return code_part + comment.rstrip() + '\n'
        return line

# Load file
print("Loading 8kbas_labeled.mac...")
with open('8kbas_labeled.mac', 'r') as f:
    lines = f.readlines()

print(f"Processing {len(lines)} lines...")

# Normalize each line
new_lines = []
changes = 0
for line in lines:
    new_line = normalize_line(line)
    if new_line != line:
        changes += 1
    new_lines.append(new_line)

print(f"Changed {changes} lines")

# Second pass: Convert all-uppercase labels to lowercase
print("Converting uppercase labels to lowercase...")

# First, find all labels defined in the file (at start of line with colon)
content = ''.join(new_lines)
defined_labels = set()
for line in new_lines:
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line)
    if m:
        defined_labels.add(m.group(1))

# Find labels that are all uppercase and should be converted
labels_to_convert = set()
for label in defined_labels:
    # Skip L0000 or D0000 style labels
    if re.match(r'^[LD][0-9A-Fa-f]{4}$', label):
        continue
    # Check if all letters are uppercase
    letters = re.sub(r'[0-9_]', '', label)
    if len(letters) > 0 and letters.isupper():
        labels_to_convert.add(label)

print(f"Found {len(labels_to_convert)} labels to convert")

# Convert each label (but not inside RDC lines or quoted strings)
for label in labels_to_convert:
    new_label = label.lower()
    # Process line by line to skip RDC lines
    for i, line in enumerate(new_lines):
        # Skip RDC lines (keyword table)
        if 'RDC' in line or 'rdc' in line:
            continue
        # Skip lines with quoted strings that might contain the label
        if "'" in line:
            continue
        # Replace whole word only
        new_lines[i] = re.sub(rf'\b{label}\b', new_label, new_lines[i])

# Write back
with open('8kbas_labeled.mac', 'w') as f:
    f.writelines(new_lines)

print("Done!")
