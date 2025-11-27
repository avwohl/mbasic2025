#!/usr/bin/env python3
"""Find where code sizes diverge by tracking offset through file."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

print(f"Reference: {len(ref)} bytes")
print(f"Ours: {len(our)} bytes")
print()

# Track position alignment through the file
# Use a sliding window to find where our position drifts from reference

last_drift = 0
scan_step = 256  # Check every 256 bytes
window = 16      # Match window size

print("Scanning for where files drift apart...")
print("File offset | Ref addr | Our addr | Drift")
print("-" * 50)

for ref_pos in range(0, len(ref) - window, scan_step):
    # Get a pattern from reference
    pattern = ref[ref_pos:ref_pos+window]

    # Search for it in our file within a reasonable range
    search_start = max(0, ref_pos - 100)
    search_end = min(len(our), ref_pos + 100)

    our_pos = our.find(pattern, search_start, search_end)

    if our_pos >= 0:
        drift = ref_pos - our_pos
        if drift != last_drift:
            print(f"0x{ref_pos:04X}     | 0x{ref_pos+0x100:04X}  | 0x{our_pos+0x100:04X}  | {drift:+d}")
            last_drift = drift
    else:
        # Pattern not found - files might be too different here
        print(f"0x{ref_pos:04X}     | Pattern not found in our file")

print()
print("Detailed scan around transition points...")

# Fine-grained scan to find exact transition
# Start from where Overflow is (both at same position) and work forward
start = 0x0400  # Just after Overflow
for ref_pos in range(start, min(len(ref), len(our)), 16):
    pattern = ref[ref_pos:ref_pos+8]

    # Try to find at same position first
    if our[ref_pos:ref_pos+8] == pattern:
        continue  # Still aligned

    # Try to find nearby
    our_pos = our.find(pattern, max(0, ref_pos-64), min(len(our), ref_pos+64))
    if our_pos >= 0:
        drift = ref_pos - our_pos
        if drift != 0:
            print(f"First drift at ref 0x{ref_pos:04X}: our pattern at 0x{our_pos:04X}, drift={drift}")

            # Show context
            print(f"  Ref bytes: {' '.join(f'{ref[j]:02X}' for j in range(ref_pos-8, ref_pos+16))}")
            print(f"  Our bytes: {' '.join(f'{our[j]:02X}' for j in range(our_pos-8, our_pos+16))}")
            break
    else:
        print(f"Pattern at ref 0x{ref_pos:04X} not found nearby in our file")
        print(f"  Ref pattern: {' '.join(f'{ref[j]:02X}' for j in range(ref_pos, ref_pos+8))}")
        break
