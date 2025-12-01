#!/usr/bin/env python3
"""
Pattern match 8K BASIC with 4K BASIC and Extended BASIC to pull in labels/comments.
Uses instruction sequence matching to find corresponding routines.
"""

import re
import os

def extract_labels_and_comments(filename):
    """Extract labels and their associated comments from a .mac file"""
    labels = {}
    current_comment = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # Check for comment block (lines starting with ;)
        if line.strip().startswith(';'):
            current_comment.append(line.rstrip())
            continue
        
        # Check for label definition
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line)
        if m:
            label = m.group(1)
            # Skip generic labels like L0123 or D0123
            if not re.match(r'^[LD][0-9A-Fa-f]{4}$', label):
                # Get the instruction after the label
                rest = line[m.end():].strip()
                labels[label] = {
                    'comment': '\n'.join(current_comment) if current_comment else '',
                    'instruction': rest,
                    'line': i
                }
        
        # Reset comment block if we hit a non-comment, non-label line
        if not line.strip().startswith(';') and not re.match(r'^([A-Za-z_][A-Za-z0-9_]*):', line):
            current_comment = []
    
    return labels

def extract_routine_signatures(filename):
    """Extract instruction sequences for routines to use for matching"""
    routines = {}
    current_label = None
    current_instructions = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        # Check for label
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)', line)
        if m:
            # Save previous routine
            if current_label and current_instructions:
                routines[current_label] = current_instructions[:10]  # First 10 instructions
            
            current_label = m.group(1)
            current_instructions = []
            
            # Get instruction on same line as label
            inst = m.group(2).strip()
            if inst and not inst.startswith(';'):
                # Normalize instruction
                inst = re.sub(r';.*', '', inst).strip()
                inst = re.sub(r'\s+', ' ', inst)
                if inst:
                    current_instructions.append(inst.upper())
        else:
            # Regular instruction line
            inst = line.strip()
            if inst and not inst.startswith(';'):
                inst = re.sub(r';.*', '', inst).strip()
                inst = re.sub(r'\s+', ' ', inst)
                if inst and current_label:
                    current_instructions.append(inst.upper())
    
    # Save last routine
    if current_label and current_instructions:
        routines[current_label] = current_instructions[:10]
    
    return routines

# Extract from 4K BASIC
print("Extracting from 4K BASIC...")
labels_4k = extract_labels_and_comments('/home/wohl/mbasic2025/4k8k/4k/4kbas40.mac')
routines_4k = extract_routine_signatures('/home/wohl/mbasic2025/4k8k/4k/4kbas40.mac')

# Extract from extended BASIC (main interpreter file)
print("Extracting from Extended BASIC...")
labels_ext = {}
routines_ext = {}
for fname in ['bintrp.mac', 'bimisc.mac', 'f4.mac', 'bistrs.mac']:
    fpath = f'/home/wohl/mbasic2025/mbasic_52/{fname}'
    if os.path.exists(fpath):
        labels_ext.update(extract_labels_and_comments(fpath))
        routines_ext.update(extract_routine_signatures(fpath))

# Extract from 8K BASIC
print("Extracting from 8K BASIC...")
routines_8k = extract_routine_signatures('/home/wohl/mbasic2025/4k8k/8k/8kbas_labeled.mac')

print(f"\n4K BASIC: {len(labels_4k)} named labels, {len(routines_4k)} routines")
print(f"Extended BASIC: {len(labels_ext)} named labels, {len(routines_ext)} routines")
print(f"8K BASIC: {len(routines_8k)} routines")

# Find matches between 8K and 4K by instruction sequence
print("\n=== Matching 8K routines to 4K BASIC ===")
matches_4k = {}
for label_8k, insts_8k in routines_8k.items():
    if len(insts_8k) < 3:
        continue
    # Normalize 8K instructions (remove specific addresses from labels)
    norm_8k = []
    for inst in insts_8k[:5]:
        # Remove label references for comparison
        norm = re.sub(r'\b[LD][0-9A-Fa-f]{4}\b', 'LABEL', inst)
        norm = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'LABEL', norm) if re.search(r'\b(JMP|CALL|JZ|JNZ|JC|JNC|LXI|LDA|STA|LHLD|SHLD)\b', norm) else norm
        norm_8k.append(norm)
    
    for label_4k, insts_4k in routines_4k.items():
        if len(insts_4k) < 3:
            continue
        norm_4k = []
        for inst in insts_4k[:5]:
            norm = re.sub(r'\b[LD][0-9A-Fa-f]{4}\b', 'LABEL', inst)
            norm = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'LABEL', norm) if re.search(r'\b(JMP|CALL|JZ|JNZ|JC|JNC|LXI|LDA|STA|LHLD|SHLD)\b', norm) else norm
            norm_4k.append(norm)
        
        # Check for match
        if norm_8k[:3] == norm_4k[:3]:
            matches_4k[label_8k] = label_4k
            break

print(f"Found {len(matches_4k)} matches with 4K BASIC")

# Output suggested label renames
print("\n=== Suggested label mappings ===")
for label_8k, label_4k in sorted(matches_4k.items()):
    if label_8k != label_4k and not re.match(r'^[LD][0-9A-Fa-f]{4}$', label_8k):
        print(f"  {label_8k} -> {label_4k}")

# Find Lxxxx labels in 8K that match named 4K labels
print("\n=== Lxxxx labels that could be named ===")
unnamed_matches = {}
for label_8k, insts_8k in routines_8k.items():
    if not re.match(r'^L[0-9A-Fa-f]{4}$', label_8k):
        continue
    if len(insts_8k) < 2:
        continue
    
    norm_8k = []
    for inst in insts_8k[:4]:
        norm = re.sub(r'\b[LD][0-9A-Fa-f]{4}\b', 'LABEL', inst)
        norm = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'LABEL', norm) if re.search(r'\b(JMP|CALL|JZ|JNZ|JC|JNC|LXI|LDA|STA|LHLD|SHLD)\b', norm) else norm
        norm_8k.append(norm)
    
    for label_4k, insts_4k in routines_4k.items():
        if re.match(r'^[LD][0-9A-Fa-f]{4}$', label_4k):
            continue
        if len(insts_4k) < 2:
            continue
        
        norm_4k = []
        for inst in insts_4k[:4]:
            norm = re.sub(r'\b[LD][0-9A-Fa-f]{4}\b', 'LABEL', inst)
            norm = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'LABEL', norm) if re.search(r'\b(JMP|CALL|JZ|JNZ|JC|JNC|LXI|LDA|STA|LHLD|SHLD)\b', norm) else norm
            norm_4k.append(norm)
        
        if norm_8k[:2] == norm_4k[:2]:
            unnamed_matches[label_8k] = (label_4k, labels_4k.get(label_4k, {}).get('comment', '')[:100])
            break

for label_8k, (label_4k, comment) in sorted(unnamed_matches.items())[:50]:
    comment_preview = comment.split('\n')[0] if comment else ''
    print(f"  {label_8k} -> {label_4k}  {comment_preview[:60]}")
