#!/usr/bin/env python3
"""Compare string/message areas between binaries."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

def find_strings(data, min_len=4):
    """Find printable string locations."""
    strings = []
    start = None
    for i, b in enumerate(data):
        if 0x20 <= b < 0x7F or b in (0x0D, 0x0A):
            if start is None:
                start = i
        else:
            if start is not None and i - start >= min_len:
                strings.append((start, data[start:i]))
            start = None
    return strings

# Find "Overflow" in both and show context
overflow_ref = ref.find(b'Overflow')
overflow_our = our.find(b'Overflow')

print("Error messages area comparison:")
print(f"Overflow at ref 0x{overflow_ref:04X}, our 0x{overflow_our:04X}")
print()

# Compare a range of bytes starting from Overflow
# This area should have error messages which are data, not code
start_ref = overflow_ref
start_our = overflow_our
compare_len = 256

print(f"Comparing {compare_len} bytes starting from 'Overflow'...")
diff_count = 0
for i in range(compare_len):
    r = ref[start_ref + i] if start_ref + i < len(ref) else -1
    o = our[start_our + i] if start_our + i < len(our) else -1
    if r != o:
        diff_count += 1
        if diff_count <= 20:
            print(f"  Diff at offset +0x{i:04X}: ref=0x{r:02X} ({chr(r) if 0x20<=r<0x7F else '?'}), our=0x{o:02X} ({chr(o) if 0x20<=o<0x7F else '?'})")

print(f"Total differences in this range: {diff_count}")
print()

# Look at the reserved word table area
# It starts right after the dispatch table
# Let's find "END" as start marker
end_ref = ref.find(b'END\x00')  # 'END' + null or high-bit set
end_our = our.find(b'END\x00')

# Actually reserved words use high-bit-set on last char
# Let's look for 'EN' + 0xC4 (D with high bit)
for i in range(len(ref) - 3):
    if ref[i:i+2] == b'EN' and ref[i+2] == 0xC4:
        end_ref = i
        break

for i in range(len(our) - 3):
    if our[i:i+2] == b'EN' and our[i+2] == 0xC4:
        end_our = i
        break

print(f"Reserved word 'END': ref 0x{end_ref:04X}, our 0x{end_our:04X}")

# Show the reserved word table
print()
print("Reserved word table start (first 100 bytes):")
print("Ref:", ' '.join(f'{ref[end_ref+i]:02X}' for i in range(min(50, len(ref)-end_ref))))
print("Our:", ' '.join(f'{our[end_our+i]:02X}' for i in range(min(50, len(our)-end_our))))

# Count length of reserved word tables
def find_reswrd_table_end(data, start):
    """Find end of reserved word table (marked by specific pattern)."""
    pos = start
    while pos < len(data) - 10:
        # Look for transition to something else
        # Reserved words have high bit set on last char
        # They're followed by address bytes
        if data[pos] == 0x80:  # Token 0x80 marks start of operators?
            return pos
        pos += 1
    return pos

# Compare reserved word data byte by byte
print()
print("Comparing reserved word tables...")
diff = 0
for i in range(200):
    r = ref[end_ref + i] if end_ref + i < len(ref) else -1
    o = our[end_our + i] if end_our + i < len(our) else -1
    if r != o:
        print(f"  Diff at res+0x{i:02X}: ref=0x{r:02X}, our=0x{o:02X}")
        diff += 1
        if diff > 20:
            break
