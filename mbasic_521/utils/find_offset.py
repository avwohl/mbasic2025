#!/usr/bin/env python3
"""Find where files diverge by looking for offset differences."""

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

# Look for the string "BASIC-80" which should be at the end
marker = b'BASIC-80'
ref_pos = ref.find(marker)
our_pos = our.find(marker)

print(f"'BASIC-80' marker:")
print(f"  In reference: 0x{ref_pos:04X}")
print(f"  In ours: 0x{our_pos:04X}")
print(f"  Offset difference: {ref_pos - our_pos}")
print()

# Look for other markers
markers = [
    b'Copyright',
    b'28-Jul-81',
    b'Bytes free',
    b'Owned by Microsoft',
]

for m in markers:
    ref_pos = ref.find(m)
    our_pos = our.find(m)
    if ref_pos >= 0 and our_pos >= 0:
        print(f"'{m.decode()}': ref=0x{ref_pos:04X}, our=0x{our_pos:04X}, diff={ref_pos - our_pos}")

print()

# Find where the offset first changes
# Start from dispatch table area and look for signature sequences
print("Looking for where offset changes...")

# The error messages near the beginning should be at same relative position
# Find "in line" or similar BASIC error message
err_marker = b'Overflow'
ref_pos = ref.find(err_marker)
our_pos = our.find(err_marker)
print(f"'Overflow' msg: ref=0x{ref_pos:04X}, our=0x{our_pos:04X}, diff={ref_pos - our_pos}")

# Find FNDFOR code pattern (look for recognizable code sequence)
# Looking for pattern near FNDFOR
print()
print("Scanning for offset changes section by section...")

# Track offset differences through the file
section_size = 0x1000
for start in range(0, min(len(ref), len(our)), section_size):
    # Find a matching pattern in this region
    sample = ref[start:start+8]
    ref_match = start
    our_match = our.find(sample, max(0, start-0x100), start+0x100)
    if our_match >= 0:
        diff = ref_match - our_match
        print(f"Section 0x{start:04X}: pattern at ref=0x{ref_match:04X}, our=0x{our_match:04X}, diff={diff}")
