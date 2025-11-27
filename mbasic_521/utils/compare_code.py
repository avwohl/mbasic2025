#!/usr/bin/env python3
"""Compare code sections by disassembling and ignoring address operands."""

# 8080 instruction info: (length, has_addr_operand)
INST_INFO = {
    0x00: (1, False), 0x01: (3, True), 0x02: (1, False), 0x03: (1, False),
    0x04: (1, False), 0x05: (1, False), 0x06: (2, False), 0x07: (1, False),
    0x08: (1, False), 0x09: (1, False), 0x0A: (1, False), 0x0B: (1, False),
    0x0C: (1, False), 0x0D: (1, False), 0x0E: (2, False), 0x0F: (1, False),
    0x10: (1, False), 0x11: (3, True), 0x12: (1, False), 0x13: (1, False),
    0x14: (1, False), 0x15: (1, False), 0x16: (2, False), 0x17: (1, False),
    0x18: (1, False), 0x19: (1, False), 0x1A: (1, False), 0x1B: (1, False),
    0x1C: (1, False), 0x1D: (1, False), 0x1E: (2, False), 0x1F: (1, False),
    0x20: (1, False), 0x21: (3, True), 0x22: (3, True), 0x23: (1, False),
    0x24: (1, False), 0x25: (1, False), 0x26: (2, False), 0x27: (1, False),
    0x28: (1, False), 0x29: (1, False), 0x2A: (3, True), 0x2B: (1, False),
    0x2C: (1, False), 0x2D: (1, False), 0x2E: (2, False), 0x2F: (1, False),
    0x30: (1, False), 0x31: (3, True), 0x32: (3, True), 0x33: (1, False),
    0x34: (1, False), 0x35: (1, False), 0x36: (2, False), 0x37: (1, False),
    0x38: (1, False), 0x39: (1, False), 0x3A: (3, True), 0x3B: (1, False),
    0x3C: (1, False), 0x3D: (1, False), 0x3E: (2, False), 0x3F: (1, False),
    # MOV instructions 0x40-0x7F
    **{i: (1, False) for i in range(0x40, 0x80)},
    # ALU instructions 0x80-0xBF
    **{i: (1, False) for i in range(0x80, 0xC0)},
    # Control instructions 0xC0-0xFF
    0xC0: (1, False), 0xC1: (1, False), 0xC2: (3, True), 0xC3: (3, True),
    0xC4: (3, True), 0xC5: (1, False), 0xC6: (2, False), 0xC7: (1, False),
    0xC8: (1, False), 0xC9: (1, False), 0xCA: (3, True), 0xCB: (2, False),
    0xCC: (3, True), 0xCD: (3, True), 0xCE: (2, False), 0xCF: (1, False),
    0xD0: (1, False), 0xD1: (1, False), 0xD2: (3, True), 0xD3: (2, False),
    0xD4: (3, True), 0xD5: (1, False), 0xD6: (2, False), 0xD7: (1, False),
    0xD8: (1, False), 0xD9: (1, False), 0xDA: (3, True), 0xDB: (2, False),
    0xDC: (3, True), 0xDD: (3, True), 0xDE: (2, False), 0xDF: (1, False),
    0xE0: (1, False), 0xE1: (1, False), 0xE2: (3, True), 0xE3: (1, False),
    0xE4: (3, True), 0xE5: (1, False), 0xE6: (2, False), 0xE7: (1, False),
    0xE8: (1, False), 0xE9: (1, False), 0xEA: (3, True), 0xEB: (1, False),
    0xEC: (3, True), 0xED: (2, False), 0xEE: (2, False), 0xEF: (1, False),
    0xF0: (1, False), 0xF1: (1, False), 0xF2: (3, True), 0xF3: (1, False),
    0xF4: (3, True), 0xF5: (1, False), 0xF6: (2, False), 0xF7: (1, False),
    0xF8: (1, False), 0xF9: (1, False), 0xFA: (3, True), 0xFB: (1, False),
    0xFC: (3, True), 0xFD: (2, False), 0xFE: (2, False), 0xFF: (1, False),
}

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

print(f"Reference: {len(ref)} bytes")
print(f"Ours: {len(our)} bytes")
print(f"Difference: {len(ref) - len(our)} bytes")
print()

# Start comparing from FNDFOR (0x0C50 memory = 0x0B50 file)
# This is where actual code begins after data tables
START = 0x0B50

ref_pos = START
our_pos = START
inst_num = 0
diffs_found = []

while ref_pos < len(ref) - 3 and our_pos < len(our) - 3:
    r_op = ref[ref_pos]
    o_op = our[our_pos]

    # Check if opcodes match
    if r_op != o_op:
        diffs_found.append({
            'type': 'opcode',
            'inst': inst_num,
            'ref_pos': ref_pos,
            'our_pos': our_pos,
            'ref_val': r_op,
            'our_val': o_op,
        })
        if len(diffs_found) >= 5:
            break
        # Try to continue - assume same length
        inst_len = INST_INFO.get(r_op, (1, False))[0]
        ref_pos += inst_len
        our_pos += inst_len
        inst_num += 1
        continue

    # Opcodes match - get instruction info
    inst_len, has_addr = INST_INFO.get(r_op, (1, False))

    # Check immediate operand for 2-byte instructions
    if inst_len == 2:
        if ref[ref_pos+1] != our[our_pos+1]:
            diffs_found.append({
                'type': 'immediate',
                'inst': inst_num,
                'ref_pos': ref_pos,
                'our_pos': our_pos,
                'opcode': r_op,
                'ref_val': ref[ref_pos+1],
                'our_val': our[our_pos+1],
            })
            if len(diffs_found) >= 5:
                break

    # For 3-byte with address, we skip the address bytes (they'll differ due to relocation)
    # But we should check if they're NOT addresses (e.g., data embedded in code)

    ref_pos += inst_len
    our_pos += inst_len
    inst_num += 1

print(f"Scanned {inst_num} instructions from 0x{START:04X}")
print(f"Ref position: 0x{ref_pos:04X}, Our position: 0x{our_pos:04X}")
print()

if diffs_found:
    print("Differences found:")
    for d in diffs_found:
        if d['type'] == 'opcode':
            print(f"  OPCODE diff at inst #{d['inst']}: ref[0x{d['ref_pos']:04X}]=0x{d['ref_val']:02X}, our[0x{d['our_pos']:04X}]=0x{d['our_val']:02X}")
            # Show context
            rp = d['ref_pos']
            op = d['our_pos']
            print(f"    Ref context: {' '.join(f'{ref[rp+i]:02X}' for i in range(-2, 10))}")
            print(f"    Our context: {' '.join(f'{our[op+i]:02X}' for i in range(-2, 10))}")
        else:
            print(f"  IMMEDIATE diff at inst #{d['inst']}: opcode=0x{d['opcode']:02X}, ref_imm=0x{d['ref_val']:02X}, our_imm=0x{d['our_val']:02X}")
            print(f"    Ref pos: 0x{d['ref_pos']:04X}, Our pos: 0x{d['our_pos']:04X}")
else:
    print("No opcode or immediate differences found in scanned range!")

# Now track where positions diverge
print()
print("Position tracking (looking for where offset drifts)...")

# Reset and scan more carefully, tracking position difference
ref_pos = START
our_pos = START
last_offset = 0

for _ in range(inst_num):
    r_op = ref[ref_pos]
    inst_len = INST_INFO.get(r_op, (1, False))[0]
    ref_pos += inst_len
    our_pos += inst_len

# After scanning same number of instructions, positions should be same if code is same size
print(f"After {inst_num} instructions: ref at 0x{ref_pos:04X}, our at 0x{our_pos:04X}")
print(f"Position difference: {ref_pos - our_pos} bytes")
