#!/usr/bin/env python3
"""Compare the end of both binaries."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

print(f"Reference: {len(ref)} bytes (ends at file 0x{len(ref)-1:04X})")
print(f"Ours: {len(our)} bytes (ends at file 0x{len(our)-1:04X})")
print(f"Difference: {len(ref) - len(our)} bytes")
print()

# Show last 100 bytes of each
print("Last 64 bytes of reference:")
for i in range(len(ref)-64, len(ref), 16):
    hex_str = ' '.join(f'{ref[j]:02X}' for j in range(i, min(i+16, len(ref))))
    print(f"  0x{i:04X}: {hex_str}")

print()
print("Last 64 bytes of ours:")
for i in range(len(our)-64, len(our), 16):
    hex_str = ' '.join(f'{our[j]:02X}' for j in range(i, min(i+16, len(our))))
    print(f"  0x{i:04X}: {hex_str}")
