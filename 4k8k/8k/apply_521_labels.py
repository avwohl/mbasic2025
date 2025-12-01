#!/usr/bin/env python3
"""
Apply labels from MBASIC 5.21 sources to 8K BASIC disassembly.
Match instruction sequences to find Lxxxx labels that should be renamed.
Also extract target labels from matching instructions.
"""

import re
import os

def normalize_inst(inst):
    """Normalize instruction for comparison"""
    inst = inst.upper().strip()
    parts = inst.split()
    if not parts:
        return ''
    opcode = parts[0]
    if len(parts) > 1:
        operand = parts[1]
        # Replace label names with LABEL but keep registers
        operand = re.sub(r'\b[A-Z][A-Z0-9_]{2,}\b', 'LABEL', operand)
        return f"{opcode} {operand}"
    return opcode

def extract_label_from_inst(inst):
    """Extract target label from instruction like 'CC negr' or 'JMP foo'"""
    inst = inst.strip()
    parts = inst.split()
    if len(parts) >= 2:
        operand = parts[1]
        # Remove any comma-separated parts
        operand = operand.split(',')[0]
        # Check if it looks like a label (not a register or number)
        if re.match(r'^[A-Za-z][A-Za-z0-9_]*$', operand):
            if operand.upper() not in ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M',
                                        'SP', 'PSW', 'BC', 'DE', 'HL']:
                return operand.lower()
    return None

def extract_labels_with_instructions(filename):
    """Extract labels with their raw instructions (not normalized)"""
    labels = {}

    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^([A-Za-z][A-Za-z0-9_]*):(.*)$', line, re.I)
        if m:
            label = m.group(1).lower()
            rest = m.group(2).strip()

            if label.startswith('$'):
                i += 1
                continue

            instructions = []  # (raw_inst, normalized_inst)

            if rest:
                inst = rest
                if ';' in rest:
                    inst = rest[:rest.index(';')].strip()
                if inst:
                    instructions.append((inst.upper(), normalize_inst(inst)))

            k = i + 1
            while k < len(lines) and len(instructions) < 5:
                next_line = lines[k].strip()
                if re.match(r'^[A-Za-z][A-Za-z0-9_]*:', next_line):
                    break
                if next_line and not next_line.startswith(';'):
                    inst = next_line
                    if ';' in next_line:
                        inst = next_line[:next_line.index(';')].strip()
                    if inst:
                        instructions.append((inst.upper(), normalize_inst(inst)))
                k += 1

            if instructions:
                labels[label] = instructions

        i += 1

    return labels

# Load 521 sources
print("Loading MBASIC 5.21 sources...")
labels_521 = {}
src_dir = '/home/wohl/mbasic2025/mbasic_521/mbasic_src'
for fname in ['f4.mac', 'bintrp.mac', 'bimisc.mac', 'bistrs.mac', 'biptrg.mac', 'bio.mac', 'biedit.mac']:
    fpath = os.path.join(src_dir, fname)
    if os.path.exists(fpath):
        file_labels = extract_labels_with_instructions(fpath)
        labels_521.update(file_labels)
        print(f"  {fname}: {len(file_labels)} labels")

print(f"Total 521 labels: {len(labels_521)}")

# Build lookup by normalized signature (first 3 instructions)
sig_to_label = {}
for label, insts in labels_521.items():
    if len(insts) >= 1:  # Allow single-instruction labels
        sig = '|'.join(norm for raw, norm in insts[:3])
        if sig not in sig_to_label:
            sig_to_label[sig] = []
        sig_to_label[sig].append((label, insts))

# Load 8K BASIC
print("\nLoading 8K BASIC...")
with open('8kbas_labeled.mac', 'r') as f:
    content = f.read()
    lines_8k = content.split('\n')

# Extract 8K labels with instructions
labels_8k = {}
i = 0
while i < len(lines_8k):
    line = lines_8k[i]
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):(.*)$', line)
    if m:
        label = m.group(1)
        rest = m.group(2).strip()

        instructions = []

        if rest:
            inst = rest
            if ';' in rest:
                inst = rest[:rest.index(';')].strip()
            if inst:
                instructions.append((inst.upper(), normalize_inst(inst)))

        k = i + 1
        while k < len(lines_8k) and len(instructions) < 5:
            next_line = lines_8k[k].strip()
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', next_line):
                break
            if next_line and not next_line.startswith(';'):
                inst = next_line
                if ';' in next_line:
                    inst = next_line[:next_line.index(';')].strip()
                if inst:
                    instructions.append((inst.upper(), normalize_inst(inst)))
            k += 1

        if instructions:
            labels_8k[label] = instructions

    i += 1

# Find renames
print("\nFinding labels to rename...")
renames = {}
used_labels = set()

# Opcodes rare enough to match on single instruction
RARE_OPCODES = {'CC', 'CNC', 'CZ', 'CNZ', 'CP', 'CM', 'CPE', 'CPO',
                'RC', 'RNC', 'RZ', 'RNZ', 'RP', 'RM', 'RPE', 'RPO'}

# First pass: find direct matches for Lxxxx labels
for label_8k, insts_8k in labels_8k.items():
    if not re.match(r'^L[0-9A-Fa-f]{4}$', label_8k):
        continue

    # Allow single instruction for rare opcodes
    first_opcode = insts_8k[0][0].split()[0] if insts_8k else ''
    min_insts = 1 if first_opcode in RARE_OPCODES else 2

    if len(insts_8k) < min_insts:
        continue

    sig = '|'.join(norm for raw, norm in insts_8k[:3])

    if sig in sig_to_label:
        candidates = sig_to_label[sig]
        valid = [(l, ins) for l, ins in candidates
                 if not re.search(rf'\b{l}:', content, re.I)
                 and l not in used_labels
                 and len(l) >= 3
                 and not l.startswith('$')]

        if len(valid) == 1:
            new_label, insts_521 = valid[0]
            renames[label_8k] = new_label
            used_labels.add(new_label)
            print(f"  {label_8k} -> {new_label}")

            # Now check for target label renames within matching instructions
            for (raw_8k, norm_8k), (raw_521, norm_521) in zip(insts_8k, insts_521):
                if norm_8k == norm_521:
                    # Extract target labels
                    target_8k = extract_label_from_inst(raw_8k)
                    target_521 = extract_label_from_inst(raw_521)

                    if target_8k and target_521:
                        # Check if 8K target is Lxxxx and 521 target is a real name
                        if (re.match(r'^l[0-9a-f]{4}$', target_8k, re.I) and
                            not re.match(r'^l[0-9a-f]{4}$', target_521, re.I) and
                            target_521 not in used_labels and
                            not re.search(rf'\b{target_521}:', content, re.I)):

                            renames[target_8k.upper()] = target_521
                            used_labels.add(target_521)
                            print(f"    -> target {target_8k.upper()} -> {target_521}")

print(f"\nFound {len(renames)} labels to rename")

# Apply renames
if renames:
    print("\nApplying renames...")

    for old_label, new_label in renames.items():
        # Replace label definition
        content = re.sub(rf'^{old_label}:', f'{new_label}:', content, flags=re.MULTILINE | re.IGNORECASE)
        # Replace references
        content = re.sub(rf'\b{old_label}\b', new_label, content, flags=re.IGNORECASE)

    with open('8kbas_labeled.mac', 'w') as f:
        f.write(content)

    print(f"Applied {len(renames)} label renames")

print("Done!")
