#!/usr/bin/env python3
"""Compare binaries byte by byte raw, find first difference."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

print(f"Reference: {len(ref)} bytes")
print(f"Ours: {len(our)} bytes")
print(f"Difference: {len(ref) - len(our)} bytes")
print()

# Find first difference
for i in range(min(len(ref), len(our))):
    if ref[i] != our[i]:
        print(f"First difference at file offset 0x{i:04X} (mem 0x{i+0x100:04X}):")
        print(f"  ref[0x{i:04X}] = 0x{ref[i]:02X}")
        print(f"  our[0x{i:04X}] = 0x{our[i]:02X}")
        print()
        # Show context around difference
        start = max(0, i-8)
        end = min(len(ref), i+24)
        print(f"Context (ref): {' '.join(f'{ref[j]:02X}' for j in range(start, end))}")
        print(f"Context (our): {' '.join(f'{our[j]:02X}' for j in range(start, min(len(our), end)))}")
        print()
        print(f"Position markers: {' '.join('^^' if j==i else '  ' for j in range(start, end))}")
        break

# Also show where files end
print()
print(f"Ref ends at 0x{len(ref):04X}")
print(f"Our ends at 0x{len(our):04X}")
