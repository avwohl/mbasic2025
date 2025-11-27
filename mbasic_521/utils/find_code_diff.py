#!/usr/bin/env python3
"""Find first code difference, ignoring relocation differences."""

import sys

# 8080 instruction lengths
INST_LEN = {
    0x00: 1, 0x01: 3, 0x02: 1, 0x03: 1, 0x04: 1, 0x05: 1, 0x06: 2, 0x07: 1,
    0x09: 1, 0x0A: 1, 0x0B: 1, 0x0C: 1, 0x0D: 1, 0x0E: 2, 0x0F: 1,
    0x11: 3, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 1, 0x16: 2, 0x17: 1,
    0x19: 1, 0x1A: 1, 0x1B: 1, 0x1C: 1, 0x1D: 1, 0x1E: 2, 0x1F: 1,
    0x21: 3, 0x22: 3, 0x23: 1, 0x24: 1, 0x25: 1, 0x26: 2, 0x27: 1,
    0x29: 1, 0x2A: 3, 0x2B: 1, 0x2C: 1, 0x2D: 1, 0x2E: 2, 0x2F: 1,
    0x31: 3, 0x32: 3, 0x33: 1, 0x34: 1, 0x35: 1, 0x36: 2, 0x37: 1,
    0x39: 1, 0x3A: 3, 0x3B: 1, 0x3C: 1, 0x3D: 1, 0x3E: 2, 0x3F: 1,
    **{i: 1 for i in range(0x40, 0x80)},  # MOV
    **{i: 1 for i in range(0x80, 0xC0)},  # ALU
    0xC0: 1, 0xC1: 1, 0xC2: 3, 0xC3: 3, 0xC4: 3, 0xC5: 1, 0xC6: 2, 0xC7: 1,
    0xC8: 1, 0xC9: 1, 0xCA: 3, 0xCB: 3, 0xCC: 3, 0xCD: 3, 0xCE: 2, 0xCF: 1,
    0xD0: 1, 0xD1: 1, 0xD2: 3, 0xD3: 2, 0xD4: 3, 0xD5: 1, 0xD6: 2, 0xD7: 1,
    0xD8: 1, 0xD9: 1, 0xDA: 3, 0xDB: 2, 0xDC: 3, 0xDD: 3, 0xDE: 2, 0xDF: 1,
    0xE0: 1, 0xE1: 1, 0xE2: 3, 0xE3: 1, 0xE4: 3, 0xE5: 1, 0xE6: 2, 0xE7: 1,
    0xE8: 1, 0xE9: 1, 0xEA: 3, 0xEB: 1, 0xEC: 3, 0xED: 3, 0xEE: 2, 0xEF: 1,
    0xF0: 1, 0xF1: 1, 0xF2: 3, 0xF3: 1, 0xF4: 3, 0xF5: 1, 0xF6: 2, 0xF7: 1,
    0xF8: 1, 0xF9: 1, 0xFA: 3, 0xFB: 1, 0xFC: 3, 0xFD: 3, 0xFE: 2, 0xFF: 1,
}

# Opcodes with 16-bit address operands (that might be relocated)
ADDR_OPCODES = {
    0x01, 0x11, 0x21, 0x31,  # LXI
    0x22, 0x2A, 0x32, 0x3A,  # SHLD, LHLD, STA, LDA
    0xC2, 0xC3, 0xC4, 0xCA, 0xCB, 0xCC, 0xCD,  # JNZ, JMP, CNZ, JZ, CZ, CALL
    0xD2, 0xD4, 0xDA, 0xDC, 0xDD,  # JNC, CNC, JC, CC
    0xE2, 0xE4, 0xEA, 0xEC, 0xED,  # JPO, CPO, JPE, CPE
    0xF2, 0xF4, 0xFA, 0xFC, 0xFD,  # JP, CP, JM, CM
}

def find_opcode_diff(ref, our):
    """Walk through both binaries comparing opcodes only."""
    pos = 0
    while pos < min(len(ref), len(our)):
        ref_op = ref[pos]
        our_op = our[pos]

        if ref_op != our_op:
            # Found a difference in opcode
            return pos, ref_op, our_op

        # Same opcode, skip operands
        length = INST_LEN.get(ref_op, 1)

        # For address opcodes, check if only the address differs
        if ref_op in ADDR_OPCODES and length == 3:
            # Compare next two bytes (address operand)
            if pos + 2 < min(len(ref), len(our)):
                ref_addr = ref[pos+1] | (ref[pos+2] << 8)
                our_addr = our[pos+1] | (our[pos+2] << 8)
                if ref_addr != our_addr:
                    # Addresses differ - this is expected due to relocation
                    # But track the offset to detect misalignment
                    pass

        pos += length

    return None, None, None

def main():
    ref = open('/home/wohl/mbasic2025/com/mbasic.com', 'rb').read()
    our = open('/home/wohl/mbasic2025/out/mbasic_order7.com', 'rb').read()

    print("Scanning for first opcode difference...")
    print()

    ref_pos = 0
    our_pos = 0
    inst_count = 0

    # Skip the initial JMP and the table after it - start at first real code
    # The table appears to end around 0x145 based on the IOGOR label
    start = 0x45  # Start after JMP at 0x100, table is at 0x103-0x144

    ref_pos = start
    our_pos = start

    while ref_pos < len(ref) and our_pos < len(our):
        ref_op = ref[ref_pos]
        our_op = our[our_pos]

        inst_count += 1

        if ref_op != our_op:
            print(f"OPCODE DIFFERENCE at instruction #{inst_count}")
            print(f"  Reference offset: 0x{ref_pos:04X} (addr 0x{ref_pos+0x100:04X}), opcode: 0x{ref_op:02X}")
            print(f"  Our build offset: 0x{our_pos:04X} (addr 0x{our_pos+0x100:04X}), opcode: 0x{our_op:02X}")
            print()

            # Show context
            print("Reference context (10 bytes before and after):")
            ctx_start = max(0, ref_pos - 10)
            ctx_end = min(len(ref), ref_pos + 20)
            hex_str = ' '.join(f'{ref[i]:02X}' for i in range(ctx_start, ctx_end))
            print(f"  {hex_str}")
            marker = '   ' * (ref_pos - ctx_start) + '^^'
            print(f"  {marker}")

            print("Our build context:")
            ctx_start = max(0, our_pos - 10)
            ctx_end = min(len(our), our_pos + 20)
            hex_str = ' '.join(f'{our[i]:02X}' for i in range(ctx_start, ctx_end))
            print(f"  {hex_str}")
            marker = '   ' * (our_pos - ctx_start) + '^^'
            print(f"  {marker}")

            break

        # Advance by instruction length
        ref_len = INST_LEN.get(ref_op, 1)
        our_len = INST_LEN.get(our_op, 1)

        # Sanity check - lengths should match if opcodes match
        if ref_len != our_len:
            print(f"WARNING: length mismatch at 0x{ref_pos:04X}")
            break

        ref_pos += ref_len
        our_pos += our_len

    if ref_pos >= len(ref) or our_pos >= len(our):
        print(f"Scanned {inst_count} instructions without finding opcode difference")
        print(f"  Reference position: 0x{ref_pos:04X}")
        print(f"  Our build position: 0x{our_pos:04X}")

if __name__ == '__main__':
    main()
