#!/usr/bin/env python3
"""Disassemble and compare two binaries around a specific offset."""

import sys

# 8080 instruction lengths
INST_LEN = {
    # 1-byte instructions
    0x00: 1, 0x01: 3, 0x02: 1, 0x03: 1, 0x04: 1, 0x05: 1, 0x06: 2, 0x07: 1,
    0x09: 1, 0x0A: 1, 0x0B: 1, 0x0C: 1, 0x0D: 1, 0x0E: 2, 0x0F: 1,
    0x11: 3, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 1, 0x16: 2, 0x17: 1,
    0x19: 1, 0x1A: 1, 0x1B: 1, 0x1C: 1, 0x1D: 1, 0x1E: 2, 0x1F: 1,
    0x21: 3, 0x22: 3, 0x23: 1, 0x24: 1, 0x25: 1, 0x26: 2, 0x27: 1,
    0x29: 1, 0x2A: 3, 0x2B: 1, 0x2C: 1, 0x2D: 1, 0x2E: 2, 0x2F: 1,
    0x31: 3, 0x32: 3, 0x33: 1, 0x34: 1, 0x35: 1, 0x36: 2, 0x37: 1,
    0x39: 1, 0x3A: 3, 0x3B: 1, 0x3C: 1, 0x3D: 1, 0x3E: 2, 0x3F: 1,
    # MOV instructions (0x40-0x7F) - all 1 byte except HLT (0x76)
    **{i: 1 for i in range(0x40, 0x80)},
    # ALU with registers (0x80-0xBF) - all 1 byte
    **{i: 1 for i in range(0x80, 0xC0)},
    # Conditional returns, pushes, calls, etc
    0xC0: 1, 0xC1: 1, 0xC2: 3, 0xC3: 3, 0xC4: 3, 0xC5: 1, 0xC6: 2, 0xC7: 1,
    0xC8: 1, 0xC9: 1, 0xCA: 3, 0xCB: 3, 0xCC: 3, 0xCD: 3, 0xCE: 2, 0xCF: 1,
    0xD0: 1, 0xD1: 1, 0xD2: 3, 0xD3: 2, 0xD4: 3, 0xD5: 1, 0xD6: 2, 0xD7: 1,
    0xD8: 1, 0xD9: 1, 0xDA: 3, 0xDB: 2, 0xDC: 3, 0xDD: 3, 0xDE: 2, 0xDF: 1,
    0xE0: 1, 0xE1: 1, 0xE2: 3, 0xE3: 1, 0xE4: 3, 0xE5: 1, 0xE6: 2, 0xE7: 1,
    0xE8: 1, 0xE9: 1, 0xEA: 3, 0xEB: 1, 0xEC: 3, 0xED: 3, 0xEE: 2, 0xEF: 1,
    0xF0: 1, 0xF1: 1, 0xF2: 3, 0xF3: 1, 0xF4: 3, 0xF5: 1, 0xF6: 2, 0xF7: 1,
    0xF8: 1, 0xF9: 1, 0xFA: 3, 0xFB: 1, 0xFC: 3, 0xFD: 3, 0xFE: 2, 0xFF: 1,
}

MNEMONICS = {
    0x00: "NOP", 0x01: "LXI B,", 0x02: "STAX B", 0x03: "INX B", 0x04: "INR B",
    0x05: "DCR B", 0x06: "MVI B,", 0x07: "RLC", 0x09: "DAD B", 0x0A: "LDAX B",
    0x0B: "DCX B", 0x0C: "INR C", 0x0D: "DCR C", 0x0E: "MVI C,", 0x0F: "RRC",
    0x11: "LXI D,", 0x12: "STAX D", 0x13: "INX D", 0x14: "INR D", 0x15: "DCR D",
    0x16: "MVI D,", 0x17: "RAL", 0x19: "DAD D", 0x1A: "LDAX D", 0x1B: "DCX D",
    0x1C: "INR E", 0x1D: "DCR E", 0x1E: "MVI E,", 0x1F: "RAR",
    0x21: "LXI H,", 0x22: "SHLD", 0x23: "INX H", 0x24: "INR H", 0x25: "DCR H",
    0x26: "MVI H,", 0x27: "DAA", 0x29: "DAD H", 0x2A: "LHLD", 0x2B: "DCX H",
    0x2C: "INR L", 0x2D: "DCR L", 0x2E: "MVI L,", 0x2F: "CMA",
    0x31: "LXI SP,", 0x32: "STA", 0x33: "INX SP", 0x34: "INR M", 0x35: "DCR M",
    0x36: "MVI M,", 0x37: "STC", 0x39: "DAD SP", 0x3A: "LDA", 0x3B: "DCX SP",
    0x3C: "INR A", 0x3D: "DCR A", 0x3E: "MVI A,", 0x3F: "CMC",
    0x76: "HLT", 0xC0: "RNZ", 0xC1: "POP B", 0xC2: "JNZ", 0xC3: "JMP",
    0xC4: "CNZ", 0xC5: "PUSH B", 0xC6: "ADI", 0xC7: "RST 0", 0xC8: "RZ",
    0xC9: "RET", 0xCA: "JZ", 0xCB: "JMP*", 0xCC: "CZ", 0xCD: "CALL",
    0xCE: "ACI", 0xCF: "RST 1", 0xD0: "RNC", 0xD1: "POP D", 0xD2: "JNC",
    0xD3: "OUT", 0xD4: "CNC", 0xD5: "PUSH D", 0xD6: "SUI", 0xD7: "RST 2",
    0xD8: "RC", 0xD9: "RET*", 0xDA: "JC", 0xDB: "IN", 0xDC: "CC",
    0xDD: "CALL*", 0xDE: "SBI", 0xDF: "RST 3", 0xE0: "RPO", 0xE1: "POP H",
    0xE2: "JPO", 0xE3: "XTHL", 0xE4: "CPO", 0xE5: "PUSH H", 0xE6: "ANI",
    0xE7: "RST 4", 0xE8: "RPE", 0xE9: "PCHL", 0xEA: "JPE", 0xEB: "XCHG",
    0xEC: "CPE", 0xED: "CALL*", 0xEE: "XRI", 0xEF: "RST 5", 0xF0: "RP",
    0xF1: "POP PSW", 0xF2: "JP", 0xF3: "DI", 0xF4: "CP", 0xF5: "PUSH PSW",
    0xF6: "ORI", 0xF7: "RST 6", 0xF8: "RM", 0xF9: "SPHL", 0xFA: "JM",
    0xFB: "EI", 0xFC: "CM", 0xFD: "CALL*", 0xFE: "CPI", 0xFF: "RST 7",
}

# MOV instructions
REGS = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
for i in range(0x40, 0x80):
    if i != 0x76:  # HLT
        dst = (i >> 3) & 7
        src = i & 7
        MNEMONICS[i] = f"MOV {REGS[dst]},{REGS[src]}"

# ALU instructions
ALU_OPS = ['ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP']
for i in range(0x80, 0xC0):
    op = (i >> 3) & 7
    reg = i & 7
    MNEMONICS[i] = f"{ALU_OPS[op]} {REGS[reg]}"

def disasm(data, start_addr, count=20):
    """Disassemble count instructions starting at offset."""
    result = []
    offset = 0
    for _ in range(count):
        if start_addr + offset >= len(data):
            break
        opcode = data[start_addr + offset]
        length = INST_LEN.get(opcode, 1)
        mnem = MNEMONICS.get(opcode, f"DB {opcode:02X}h")

        addr = 0x100 + start_addr + offset
        hex_bytes = ' '.join(f'{data[start_addr + offset + i]:02X}' for i in range(length) if start_addr + offset + i < len(data))

        if length == 2:
            operand = data[start_addr + offset + 1] if start_addr + offset + 1 < len(data) else 0
            inst = f"{mnem}{operand:02X}h"
        elif length == 3:
            lo = data[start_addr + offset + 1] if start_addr + offset + 1 < len(data) else 0
            hi = data[start_addr + offset + 2] if start_addr + offset + 2 < len(data) else 0
            val = (hi << 8) | lo
            inst = f"{mnem}{val:04X}h"
        else:
            inst = mnem

        result.append((addr, hex_bytes, inst))
        offset += length
    return result

def main():
    ref_file = '/home/wohl/mbasic2025/com/mbasic.com'
    our_file = '/home/wohl/mbasic2025/out/mbasic_order7.com'

    with open(ref_file, 'rb') as f:
        ref_data = f.read()
    with open(our_file, 'rb') as f:
        our_data = f.read()

    # Find first difference
    first_diff = None
    for i in range(min(len(ref_data), len(our_data))):
        if ref_data[i] != our_data[i]:
            first_diff = i
            break

    if first_diff is None:
        print("Files are identical!")
        return

    print(f"First difference at offset 0x{first_diff:04X} (address 0x{first_diff+0x100:04X})")
    print(f"Reference: {ref_data[first_diff]:02X}, Our build: {our_data[first_diff]:02X}")
    print()

    # Find a sync point before the difference
    # Look backwards for a matching sequence
    sync_start = max(0, first_diff - 50)

    print(f"=== Reference binary (5.21) starting at 0x{sync_start+0x100:04X} ===")
    for addr, hex_bytes, inst in disasm(ref_data, sync_start, 30):
        marker = " <-- DIFF" if addr - 0x100 == first_diff else ""
        print(f"{addr:04X}: {hex_bytes:12s}  {inst}{marker}")

    print()
    print(f"=== Our build (5.22) starting at 0x{sync_start+0x100:04X} ===")
    for addr, hex_bytes, inst in disasm(our_data, sync_start, 30):
        marker = " <-- DIFF" if addr - 0x100 == first_diff else ""
        print(f"{addr:04X}: {hex_bytes:12s}  {inst}{marker}")

if __name__ == '__main__':
    main()
