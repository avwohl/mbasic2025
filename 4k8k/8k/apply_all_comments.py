#!/usr/bin/env python3
"""
Apply comments from both MBASIC 5.21 and 4K BASIC sources to 8K BASIC.
Match instruction sequences to apply inline comments.
Also apply block comments before routines.
"""

import re
import os

# Register pair synonyms (ud80 uses HL/DE/BC, sources might use H/D/B)
REG_PAIRS = {
    'HL': 'H', 'DE': 'D', 'BC': 'B',
    'H': 'H', 'D': 'D', 'B': 'B',
    'SP': 'SP', 'PSW': 'PSW'
}

def normalize_inst(inst):
    """Normalize instruction for comparison"""
    inst = inst.upper().strip()
    if ';' in inst:
        inst = inst[:inst.index(';')].strip()

    parts = inst.split()
    if not parts:
        return ''

    opcode = parts[0]

    # Skip non-instructions
    if opcode in ('DB', 'DW', 'DS', 'EQU', 'ORG', 'END', 'PUBLIC', 'EXTRN', 'RDC', 'SUBTTL', 'TITLE', 'ASEG', 'CSEG', 'DSEG'):
        return ''

    if len(parts) == 1:
        return opcode

    operand = parts[1]

    # Normalize register pairs for DAD, DCX, INX, PUSH, POP, LXI, LDAX, STAX
    if opcode in ('DAD', 'DCX', 'INX', 'PUSH', 'POP', 'LXI', 'LDAX', 'STAX'):
        reg = operand.split(',')[0].strip()
        if reg in REG_PAIRS:
            operand = REG_PAIRS[reg]
            if ',' in parts[1]:
                rest = parts[1].split(',', 1)[1]
                operand = operand + ',' + re.sub(r'\b[A-Z][A-Z0-9_]{2,}\b', 'LABEL', rest)
    else:
        # Replace label names with LABEL placeholder but keep register names
        operand = re.sub(r'\b[A-Z][A-Z0-9_]{2,}\b', 'LABEL', operand)

    return f"{opcode} {operand}"

def extract_all_instructions(filename):
    """Extract all instructions with their comments from a file"""
    instructions = []  # List of (normalized_inst, raw_inst, comment)

    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(';'):
            continue

        # Remove label prefix if present
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', stripped):
            stripped = re.sub(r'^[A-Za-z_][A-Za-z0-9_]*:\s*', '', stripped)

        if not stripped or stripped.startswith(';'):
            continue

        # Extract instruction and comment
        inst = stripped
        comment = ''
        if ';' in stripped:
            idx = stripped.index(';')
            inst = stripped[:idx].strip()
            comment = stripped[idx:].strip()

        if inst:
            norm = normalize_inst(inst)
            if norm:
                instructions.append((norm, inst.upper(), comment))

    return instructions

def extract_routines_with_block_comments(filename):
    """Extract routines with their block comments and instructions"""
    routines = {}

    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for label definition
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$', line, re.I)
        if m:
            label = m.group(1).lower()
            rest = m.group(2)

            # Get preceding comment block
            block_comments = []
            j = i - 1
            while j >= 0:
                prev = lines[j].rstrip()
                if prev.strip().startswith(';') or prev.strip() == '':
                    if prev.strip():
                        block_comments.insert(0, prev)
                    j -= 1
                else:
                    break

            # Get instructions with comments
            instructions = []
            if rest.strip() and not rest.strip().startswith(';'):
                inst = rest
                comment = ''
                if ';' in rest:
                    idx = rest.index(';')
                    inst = rest[:idx].strip()
                    comment = rest[idx:].strip()
                if inst:
                    norm = normalize_inst(inst)
                    if norm:
                        instructions.append((norm, inst.upper(), comment))

            k = i + 1
            while k < len(lines) and len(instructions) < 30:
                next_line = lines[k]
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', next_line):
                    break

                next_stripped = next_line.strip()
                if next_stripped.startswith(';'):
                    k += 1
                    continue

                if next_stripped:
                    inst = next_stripped
                    comment = ''
                    if ';' in next_stripped:
                        idx = next_stripped.index(';')
                        inst = next_stripped[:idx].strip()
                        comment = next_stripped[idx:].strip()
                    if inst:
                        norm = normalize_inst(inst)
                        if norm:
                            instructions.append((norm, inst.upper(), comment))
                k += 1

            if instructions:
                routines[label] = {
                    'block_comment': '\n'.join(block_comments),
                    'instructions': instructions
                }

        i += 1

    return routines

def build_signature_index(instructions, window=5):
    """Build index of instruction signatures for fast lookup"""
    index = {}

    for i in range(len(instructions) - window + 1):
        sig = tuple(inst[0] for inst in instructions[i:i+window])
        if sig not in index:
            index[sig] = []
        index[sig].append((i, instructions[i:i+window+15]))

    return index

# Load sources from both 521 and 4K
print("Loading source files...")

all_insts = []
all_routines = {}

# 4K BASIC (often has better block comments)
fpath = '/home/wohl/mbasic2025/4k8k/4k/4kbas40.mac'
if os.path.exists(fpath):
    insts = extract_all_instructions(fpath)
    all_insts.extend(insts)
    routines = extract_routines_with_block_comments(fpath)
    all_routines.update(routines)
    print(f"  4kbas40.mac: {len(insts)} instructions, {len(routines)} routines")

# 521 BASIC sources
src_dir = '/home/wohl/mbasic2025/mbasic_521/mbasic_src'
for fname in ['f4.mac', 'bintrp.mac', 'bimisc.mac', 'bistrs.mac', 'biptrg.mac', 'bio.mac', 'biedit.mac']:
    fpath = os.path.join(src_dir, fname)
    if os.path.exists(fpath):
        insts = extract_all_instructions(fpath)
        all_insts.extend(insts)
        routines = extract_routines_with_block_comments(fpath)
        # Don't overwrite 4K comments which are often better
        for label, data in routines.items():
            if label not in all_routines:
                all_routines[label] = data
        print(f"  {fname}: {len(insts)} instructions, {len(routines)} routines")

print(f"Total: {len(all_insts)} instructions, {len(all_routines)} routines")

# Build signature index
print("Building signature index...")
sig_index = build_signature_index(all_insts, window=5)
print(f"Unique 5-instruction signatures: {len(sig_index)}")

# Load 8K BASIC
print("\nLoading 8K BASIC...")
with open('8kbas_labeled.mac', 'r') as f:
    lines_8k = f.readlines()

# Extract 8K instructions with line numbers
insts_8k = []
for i, line in enumerate(lines_8k):
    stripped = line.strip()
    if not stripped or stripped.startswith(';'):
        continue

    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', stripped):
        stripped = re.sub(r'^[A-Za-z_][A-Za-z0-9_]*:\s*', '', stripped)

    if not stripped or stripped.startswith(';'):
        continue

    inst = stripped
    has_comment = ';' in stripped
    if has_comment:
        inst = stripped[:stripped.index(';')].strip()

    if inst:
        norm = normalize_inst(inst)
        if norm:
            insts_8k.append((i, norm, inst.upper(), has_comment))

print(f"8K instructions: {len(insts_8k)}")

# First pass: Match and apply inline comments (before any insertions)
print("\nMatching instruction sequences...")
changes = 0
matched_sequences = 0
i = 0

while i < len(insts_8k) - 4:
    sig = tuple(inst[1] for inst in insts_8k[i:i+5])

    if sig in sig_index:
        matches = sig_index[sig]
        best_match = None
        best_len = 0

        for start_idx, match_insts in matches:
            match_len = 0
            for j, (norm_8k, match_inst) in enumerate(zip(
                [x[1] for x in insts_8k[i:i+25]],
                [x[0] for x in match_insts]
            )):
                if norm_8k == match_inst:
                    match_len += 1
                else:
                    break

            if match_len > best_len:
                best_len = match_len
                best_match = match_insts

        if best_match and best_len >= 5:
            matched_sequences += 1

            for j in range(best_len):
                if i + j >= len(insts_8k):
                    break

                line_num, norm, raw, has_comment = insts_8k[i + j]

                if has_comment:
                    continue

                if j < len(best_match):
                    _, _, comment_src = best_match[j]
                    if comment_src:
                        old_line = lines_8k[line_num].rstrip()
                        if ';' in old_line:
                            old_line = old_line[:old_line.index(';')].rstrip()
                        # Align comments at column 40
                        if len(old_line) < 40:
                            old_line = old_line.ljust(40)
                        else:
                            old_line = old_line + ' '
                        lines_8k[line_num] = old_line + comment_src + '\n'
                        changes += 1

            i += best_len
            continue

    i += 1

print(f"\nMatched {matched_sequences} instruction sequences")
print(f"Applied {changes} inline comments")

# Second pass: Apply block comments (insert from bottom to top to preserve line numbers)
print("\nApplying block comments to routines...")

# Parse 8K labels with line numbers
labels_8k = []
for i, line in enumerate(lines_8k):
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line)
    if m:
        labels_8k.append((i, m.group(1).lower()))

# Sort by line number descending so insertions don't affect earlier lines
labels_8k.sort(key=lambda x: -x[0])

block_comments_added = 0
for line_num, label in labels_8k:
    if label in all_routines:
        block_comment = all_routines[label]['block_comment']
        if block_comment and block_comment.strip():
            # Check if there's already a block comment
            has_block = False
            j = line_num - 1
            while j >= 0 and j >= line_num - 5:
                prev = lines_8k[j].strip()
                if prev.startswith(';=') or prev.startswith('; ==='):
                    has_block = True
                    break
                if prev and not prev.startswith(';'):
                    break
                j -= 1

            if not has_block:
                # Insert block comment before the label
                lines_8k.insert(line_num, block_comment + '\n')
                block_comments_added += 1

print(f"Added {block_comments_added} block comments")

# Third pass: Realign all inline comments to column 40
print("\nRealigning comments to column 40...")
realigned = 0
for i, line in enumerate(lines_8k):
    # Skip pure comment lines (starting with ;)
    stripped = line.lstrip()
    if stripped.startswith(';'):
        continue

    # Skip lines without inline comments
    if ';' not in line:
        continue

    # Split code and comment
    idx = line.index(';')
    code_part = line[:idx].rstrip()
    comment_part = line[idx:].rstrip()

    # Skip if it's a block comment continuation or hex comment on DB/DW
    if not code_part.strip():
        continue

    # Realign to column 40
    if len(code_part) < 40:
        new_line = code_part.ljust(40) + comment_part + '\n'
    else:
        new_line = code_part + ' ' + comment_part + '\n'

    if new_line != line:
        lines_8k[i] = new_line
        realigned += 1

print(f"Realigned {realigned} comments")

# Write back
with open('8kbas_labeled.mac', 'w') as f:
    f.writelines(lines_8k)

print("Done!")
