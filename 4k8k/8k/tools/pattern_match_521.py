#!/usr/bin/env python3
"""
Pattern match 8K BASIC with MBASIC 5.21 sources to pull in labels/comments.
"""

import re
import os

def extract_labels_with_context(filename):
    """Extract labels, comments, and surrounding context from a .mac file"""
    labels = {}
    
    with open(filename, 'r', errors='ignore') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for label definition (not local labels starting with $)
        m = re.match(r'^([A-Za-z][A-Za-z0-9]*):(.*)$', line, re.I)
        if m:
            label = m.group(1).lower()
            rest = m.group(2).strip()
            
            # Get preceding comment block
            comment_lines = []
            j = i - 1
            while j >= 0 and (lines[j].strip().startswith(';') or lines[j].strip() == ''):
                if lines[j].strip().startswith(';'):
                    comment_lines.insert(0, lines[j].rstrip())
                j -= 1
            
            # Get inline comment
            inline_comment = ''
            if ';' in rest:
                inline_comment = rest[rest.index(';'):]
                rest = rest[:rest.index(';')].strip()
            
            # Get following instructions (up to 8)
            instructions = []
            if rest and not rest.startswith(';'):
                instructions.append(rest.upper())
            
            k = i + 1
            while k < len(lines) and len(instructions) < 8:
                next_line = lines[k].strip()
                if re.match(r'^[A-Za-z][A-Za-z0-9]*:', next_line):
                    break  # Hit next label
                if next_line and not next_line.startswith(';'):
                    # Remove comment part
                    inst = re.sub(r';.*', '', next_line).strip()
                    if inst:
                        instructions.append(inst.upper())
                k += 1
            
            labels[label] = {
                'comment': '\n'.join(comment_lines),
                'inline': inline_comment,
                'instructions': instructions
            }
        i += 1
    
    return labels

def normalize_instruction(inst):
    """Normalize instruction for comparison"""
    # Remove labels from jumps/calls, keep opcode and register operands
    inst = inst.upper()
    inst = re.sub(r';.*', '', inst).strip()
    
    # Replace any label references with LABEL placeholder
    # But keep immediate values and register names
    inst = re.sub(r'\b[A-Z][A-Z0-9]*\b(?=\s*$)', 'LABEL', inst)  # trailing label
    inst = re.sub(r',\s*[A-Z][A-Z0-9]+\s*$', ',LABEL', inst)  # label after comma
    
    return inst.strip()

def match_routines(labels_521, routines_8k):
    """Match 8K routines to 521 labels by instruction sequence"""
    matches = {}
    
    for label_8k, insts_8k in routines_8k.items():
        if len(insts_8k) < 2:
            continue
            
        # Normalize 8K instructions
        norm_8k = [normalize_instruction(i) for i in insts_8k[:5]]
        
        best_match = None
        best_score = 0
        
        for label_521, data in labels_521.items():
            insts_521 = data['instructions']
            if len(insts_521) < 2:
                continue
            
            norm_521 = [normalize_instruction(i) for i in insts_521[:5]]
            
            # Count matching instructions
            score = 0
            for n8, n5 in zip(norm_8k, norm_521):
                if n8 == n5:
                    score += 1
                else:
                    break
            
            if score >= 2 and score > best_score:
                best_score = score
                best_match = label_521
        
        if best_match:
            matches[label_8k] = (best_match, best_score, labels_521[best_match])
    
    return matches

# Extract from 521 BASIC sources
print("Extracting from MBASIC 5.21 sources...")
labels_521 = {}
src_dir = '/home/wohl/mbasic2025/mbasic_521/mbasic_src'
for fname in ['bintrp.mac', 'bimisc.mac', 'f4.mac', 'bistrs.mac', 'biptrg.mac', 'bio.mac', 'biedit.mac']:
    fpath = os.path.join(src_dir, fname)
    if os.path.exists(fpath):
        file_labels = extract_labels_with_context(fpath)
        print(f"  {fname}: {len(file_labels)} labels")
        labels_521.update(file_labels)

print(f"\nTotal 521 labels: {len(labels_521)}")

# Extract routines from 8K BASIC
print("\nExtracting from 8K BASIC...")
with open('/home/wohl/mbasic2025/4k8k/8k/8kbas_labeled.mac', 'r') as f:
    lines = f.readlines()

routines_8k = {}
current_label = None
current_insts = []

for line in lines:
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)', line)
    if m:
        if current_label:
            routines_8k[current_label] = current_insts
        current_label = m.group(1)
        current_insts = []
        rest = m.group(2).strip()
        if rest and not rest.startswith(';'):
            rest = re.sub(r';.*', '', rest).strip()
            if rest:
                current_insts.append(rest.upper())
    elif current_label:
        inst = line.strip()
        if inst and not inst.startswith(';'):
            inst = re.sub(r';.*', '', inst).strip()
            if inst:
                current_insts.append(inst.upper())

if current_label:
    routines_8k[current_label] = current_insts

print(f"8K BASIC routines: {len(routines_8k)}")

# Match
print("\nMatching routines...")
matches = match_routines(labels_521, routines_8k)

# Show matches for Lxxxx labels (unnamed in 8K)
print("\n=== Unnamed 8K labels matching 521 labels ===")
unnamed_matches = [(k, v) for k, v in matches.items() if re.match(r'^L[0-9A-Fa-f]{4}$', k)]
unnamed_matches.sort(key=lambda x: x[0])

for label_8k, (label_521, score, data) in unnamed_matches[:80]:
    comment = data['comment'].split('\n')[0][:60] if data['comment'] else ''
    inline = data['inline'][:40] if data['inline'] else ''
    print(f"{label_8k} -> {label_521:20} (score={score}) {inline or comment}")

# Show all matches with comments for adding to source
print("\n\n=== Label rename suggestions ===")
for label_8k, (label_521, score, data) in sorted(matches.items()):
    if score >= 3 and re.match(r'^L[0-9A-Fa-f]{4}$', label_8k):
        print(f"-e {label_8k[1:]},{label_521}")
