#!/usr/bin/env python3
"""Show bytes at specific offset in both files."""
import sys

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

offset = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x0F7A

print(f"File offset: 0x{offset:04X} (Memory: 0x{offset+0x100:04X})")
print()

# Show 32 bytes around this offset
start = max(0, offset - 16)
end = min(len(ref), offset + 16)

print(f"Reference (0x{start:04X} - 0x{end-1:04X}):")
for i in range(start, end, 16):
    hex_str = ' '.join(f'{ref[j]:02X}' for j in range(i, min(i+16, end)))
    print(f"  0x{i:04X}: {hex_str}")

print()
print(f"Ours (0x{start:04X} - 0x{end-1:04X}):")
for i in range(start, end, 16):
    hex_str = ' '.join(f'{our[j]:02X}' for j in range(i, min(i+16, len(our))))
    print(f"  0x{i:04X}: {hex_str}")

print()
print("Byte-by-byte comparison:")
for i in range(start, end):
    r = ref[i] if i < len(ref) else 0
    o = our[i] if i < len(our) else 0
    marker = " <-- DIFF" if r != o else ""
    print(f"  0x{i:04X}: ref=0x{r:02X} our=0x{o:02X}{marker}")
