#!/usr/bin/env python3
"""
Apply comments from MBASIC 5.21 sources to 8K BASIC disassembly.
Match instruction sequences to apply inline comments.
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
    if opcode in ('DB', 'DW', 'DS', 'EQU', 'ORG', 'END', 'PUBLIC', 'EXTRN', 'RDC', 'SUBTTL', 'TITLE'):
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
        # Skip label-only lines
        stripped = line.strip()
        if not stripped or stripped.startswith(';'):
            continue

        # Remove label prefix if present
        if re.match(r'^[A-Za-z][A-Za-z0-9_]*:', stripped):
            stripped = re.sub(r'^[A-Za-z][A-Za-z0-9_]*:\s*', '', stripped)

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
            if norm:  # Skip DB/DW/etc
                instructions.append((norm, inst.upper(), comment))

    return instructions

def build_signature_index(instructions, window=5):
    """Build index of instruction signatures for fast lookup"""
    index = {}  # signature -> list of (start_idx, instructions)

    for i in range(len(instructions) - window + 1):
        sig = tuple(inst[0] for inst in instructions[i:i+window])
        if sig not in index:
            index[sig] = []
        index[sig].append((i, instructions[i:i+window+10]))  # Keep extra for more matching

    return index

# Load 521 sources
print("Loading MBASIC 5.21 sources...")
all_521_insts = []
src_dir = '/home/wohl/mbasic2025/mbasic_521/mbasic_src'
for fname in ['f4.mac', 'bintrp.mac', 'bimisc.mac', 'bistrs.mac', 'biptrg.mac', 'bio.mac', 'biedit.mac']:
    fpath = os.path.join(src_dir, fname)
    if os.path.exists(fpath):
        insts = extract_all_instructions(fpath)
        all_521_insts.extend(insts)
        print(f"  {fname}: {len(insts)} instructions")

print(f"Total 521 instructions: {len(all_521_insts)}")

# Build signature index
print("Building signature index...")
sig_index = build_signature_index(all_521_insts, window=5)
print(f"Unique 5-instruction signatures: {len(sig_index)}")

# Load 8K BASIC
print("\nLoading 8K BASIC...")
with open('8kbas_labeled.mac', 'r') as f:
    lines_8k = f.readlines()

# Extract 8K instructions with line numbers
insts_8k = []  # List of (line_num, normalized, raw, has_comment)
for i, line in enumerate(lines_8k):
    stripped = line.strip()
    if not stripped or stripped.startswith(';'):
        continue

    # Remove label prefix if present
    orig_stripped = stripped
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', stripped):
        stripped = re.sub(r'^[A-Za-z_][A-Za-z0-9_]*:\s*', '', stripped)

    if not stripped or stripped.startswith(';'):
        continue

    # Extract instruction
    inst = stripped
    has_comment = ';' in stripped
    if has_comment:
        inst = stripped[:stripped.index(';')].strip()

    if inst:
        norm = normalize_inst(inst)
        if norm:
            insts_8k.append((i, norm, inst.upper(), has_comment))

print(f"8K instructions: {len(insts_8k)}")

# Match and apply comments
print("\nMatching instruction sequences...")
changes = 0
matched_sequences = 0
i = 0

while i < len(insts_8k) - 4:
    # Build 5-instruction signature at this position
    sig = tuple(inst[1] for inst in insts_8k[i:i+5])

    if sig in sig_index:
        # Found a match - try to extend it
        matches = sig_index[sig]
        best_match = None
        best_len = 0

        for start_idx, match_insts in matches:
            # Count how many instructions match
            match_len = 0
            for j, (norm_8k, match_inst) in enumerate(zip(
                [x[1] for x in insts_8k[i:i+20]],
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

            # Apply comments from the matched sequence
            for j in range(best_len):
                if i + j >= len(insts_8k):
                    break

                line_num, norm, raw, has_comment = insts_8k[i + j]

                if has_comment:
                    continue  # Already has a comment

                if j < len(best_match):
                    _, _, comment_521 = best_match[j]
                    if comment_521:
                        # Add the comment
                        old_line = lines_8k[line_num].rstrip()
                        if ';' in old_line:
                            old_line = old_line[:old_line.index(';')].rstrip()
                        if len(old_line) < 32:
                            old_line = old_line.ljust(32)
                        else:
                            old_line = old_line + '\t'
                        lines_8k[line_num] = old_line + comment_521 + '\n'
                        changes += 1

            # Skip past this matched sequence
            i += best_len
            continue

    i += 1

print(f"\nMatched {matched_sequences} instruction sequences")
print(f"Applied {changes} comments")

# Write back
with open('8kbas_labeled.mac', 'w') as f:
    f.writelines(lines_8k)

print("Done!")
