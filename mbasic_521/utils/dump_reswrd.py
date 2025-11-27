#!/usr/bin/env python3
"""Dump the reserved word table from both binaries."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

def decode_reswrd(data, start, max_words=100):
    """Decode reserved word table - words have high bit set on last char."""
    pos = start
    words = []
    while len(words) < max_words and pos < len(data) - 1:
        word = ""
        word_start = pos
        while pos < len(data):
            b = data[pos]
            if b & 0x80:  # High bit set - last char
                word += chr(b & 0x7F)
                pos += 1
                break
            elif b >= 0x20 and b < 0x7F:
                word += chr(b)
                pos += 1
            else:
                # Not a character - might be end of table or data
                break

        if word:
            words.append((word_start, word))
        else:
            # Skip non-word byte and try again (might be addresses)
            pos += 1
            if pos - start > 2000:  # Safety limit
                break

    return words

# Find start of reserved word text table
# Look for "END" with high bit on last char near start of file
for i in range(0x200, 0x800):
    if ref[i:i+2] == b'EN' and ref[i+2] == 0xC4:  # 'D' with high bit
        ref_start = i
        break

for i in range(0x200, 0x800):
    if our[i:i+2] == b'EN' and our[i+2] == 0xC4:
        our_start = i
        break

print(f"Reserved word text table:")
print(f"  Reference starts at: 0x{ref_start:04X}")
print(f"  Ours starts at: 0x{our_start:04X}")
print()

# Manually parse the reserved words from each
# The format seems to be: word(with high bit on last) followed by other data

# Let me just show raw bytes side by side
print("Raw bytes starting from END:")
print("Offset | Ref               | Our")
print("-" * 60)

for i in range(0, 200, 8):
    ref_bytes = ' '.join(f'{ref[ref_start+i+j]:02X}' for j in range(8) if ref_start+i+j < len(ref))
    our_bytes = ' '.join(f'{our[our_start+i+j]:02X}' for j in range(8) if our_start+i+j < len(our))
    diff_marker = " DIFF" if ref[ref_start+i:ref_start+i+8] != our[our_start+i:our_start+i+8] else ""
    print(f"0x{i:03X}  | {ref_bytes:23s} | {our_bytes:23s}{diff_marker}")

print()
print("Interpreting reserved words:")

# The structure appears to be:
# - Reserved word text with high bit set on last char
# - Possibly address bytes after each word
# Let me look for a different pattern - the dispatch table addresses

# Actually, let's look at the statement dispatch table which comes before the reserved words
# Find the JMP instruction at start (0x100) and follow to find structure

print()
print("Structure analysis:")
print("JMP at start:", ' '.join(f'{ref[0]:02X} {ref[1]:02X} {ref[2]:02X}'))
print("Next bytes:", ' '.join(f'{ref[i]:02X}' for i in range(3, 20)))

# The dispatch table is a series of DW (2-byte addresses)
# Count how many entries before reserved word text
print()
print("Dispatch table (2-byte addresses):")
for i in range(3, 100, 2):
    addr = ref[i] + (ref[i+1] << 8)
    print(f"  0x{i:03X}: 0x{addr:04X}")
    if i > 50:
        break
