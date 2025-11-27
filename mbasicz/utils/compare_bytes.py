#!/usr/bin/env python3
"""Compare binaries byte by byte, skipping address operands."""

# 8080 instruction lengths (0=prefix for Z80 extended)
INST_LEN = {
    0x00: 1, 0x01: 3, 0x02: 1, 0x03: 1, 0x04: 1, 0x05: 1, 0x06: 2, 0x07: 1,
    0x08: 1, 0x09: 1, 0x0A: 1, 0x0B: 1, 0x0C: 1, 0x0D: 1, 0x0E: 2, 0x0F: 1,
    0x10: 1, 0x11: 3, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 1, 0x16: 2, 0x17: 1,
    0x18: 1, 0x19: 1, 0x1A: 1, 0x1B: 1, 0x1C: 1, 0x1D: 1, 0x1E: 2, 0x1F: 1,
    0x20: 1, 0x21: 3, 0x22: 3, 0x23: 1, 0x24: 1, 0x25: 1, 0x26: 2, 0x27: 1,
    0x28: 1, 0x29: 1, 0x2A: 3, 0x2B: 1, 0x2C: 1, 0x2D: 1, 0x2E: 2, 0x2F: 1,
    0x30: 1, 0x31: 3, 0x32: 3, 0x33: 1, 0x34: 1, 0x35: 1, 0x36: 2, 0x37: 1,
    0x38: 1, 0x39: 1, 0x3A: 3, 0x3B: 1, 0x3C: 1, 0x3D: 1, 0x3E: 2, 0x3F: 1,
    **{i: 1 for i in range(0x40, 0x80)},  # MOV instructions
    **{i: 1 for i in range(0x80, 0xC0)},  # ALU instructions
    0xC0: 1, 0xC1: 1, 0xC2: 3, 0xC3: 3, 0xC4: 3, 0xC5: 1, 0xC6: 2, 0xC7: 1,
    0xC8: 1, 0xC9: 1, 0xCA: 3, 0xCB: 2, 0xCC: 3, 0xCD: 3, 0xCE: 2, 0xCF: 1,
    0xD0: 1, 0xD1: 1, 0xD2: 3, 0xD3: 2, 0xD4: 3, 0xD5: 1, 0xD6: 2, 0xD7: 1,
    0xD8: 1, 0xD9: 1, 0xDA: 3, 0xDB: 2, 0xDC: 3, 0xDD: 3, 0xDE: 2, 0xDF: 1,
    0xE0: 1, 0xE1: 1, 0xE2: 3, 0xE3: 1, 0xE4: 3, 0xE5: 1, 0xE6: 2, 0xE7: 1,
    0xE8: 1, 0xE9: 1, 0xEA: 3, 0xEB: 1, 0xEC: 3, 0xED: 2, 0xEE: 2, 0xEF: 1,
    0xF0: 1, 0xF1: 1, 0xF2: 3, 0xF3: 1, 0xF4: 3, 0xF5: 1, 0xF6: 2, 0xF7: 1,
    0xF8: 1, 0xF9: 1, 0xFA: 3, 0xFB: 1, 0xFC: 3, 0xFD: 2, 0xFE: 2, 0xFF: 1,
}

# Instructions with 16-bit address operands (skip these operands during compare)
ADDR_OPS = {0x01, 0x11, 0x21, 0x31,  # LXI
            0x22, 0x2A, 0x32, 0x3A,  # SHLD, LHLD, STA, LDA
            0xC2, 0xC3, 0xC4, 0xCA, 0xCC, 0xCD,  # JNZ, JMP, CNZ, JZ, CZ, CALL
            0xD2, 0xD4, 0xDA, 0xDC, 0xDD,  # JNC, CNC, JC, CC, (DD)
            0xE2, 0xE4, 0xEA, 0xEC,  # JPO, CPO, JPE, CPE
            0xF2, 0xF4, 0xFA, 0xFC}  # JP, CP, JM, CM

ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
our = open('/home/wohl/mbasic2025/out/mbasic_go.com', 'rb').read()

print(f"Reference: {len(ref)} bytes")
print(f"Ours: {len(our)} bytes")
print(f"Difference: {len(ref) - len(our)} bytes")
print()

# Start from beginning of code area
pos = 0
inst_count = 0
diffs = []

while pos < len(ref) and pos < len(our) and len(diffs) < 20:
    r_op = ref[pos]
    o_op = our[pos]

    if r_op != o_op:
        diffs.append(f"OPCODE diff at file 0x{pos:04X} (mem 0x{pos+0x100:04X}): ref={r_op:02X}, our={o_op:02X}")
        # Try to continue by assuming same length
        inst_len = INST_LEN.get(r_op, 1)
        pos += inst_len
        inst_count += 1
        continue

    inst_len = INST_LEN.get(r_op, 1)

    # Check immediate byte for 2-byte instructions (not addresses)
    if inst_len == 2 and r_op not in ADDR_OPS:
        if pos + 1 < len(ref) and pos + 1 < len(our):
            if ref[pos+1] != our[pos+1]:
                diffs.append(f"IMMEDIATE diff at file 0x{pos:04X} (mem 0x{pos+0x100:04X}): op={r_op:02X}, ref_imm={ref[pos+1]:02X}, our_imm={our[pos+1]:02X}")

    # Skip address operands for 3-byte instructions
    # (they will differ due to relocation)

    pos += inst_len
    inst_count += 1

print(f"Scanned {inst_count} instructions")
print(f"Final position: file 0x{pos:04X} (mem 0x{pos+0x100:04X})")
print()

if diffs:
    print("First differences found:")
    for d in diffs[:10]:
        print(f"  {d}")
else:
    print("No opcode/immediate differences found in overlapping region!")
