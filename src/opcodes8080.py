"""
8080 CPU instruction definitions for um80 assembler.
"""

# Register encodings (3-bit)
REGS = {
    'B': 0, 'C': 1, 'D': 2, 'E': 3, 'H': 4, 'L': 5, 'M': 6, 'A': 7
}

# Register pair encodings (2-bit) for PUSH/POP
REGPAIRS_PUSHPOP = {
    'B': 0, 'BC': 0, 'D': 1, 'DE': 1, 'H': 2, 'HL': 2, 'PSW': 3
}

# Register pair encodings (2-bit) for LXI/DAD/INX/DCX/LDAX/STAX
REGPAIRS = {
    'B': 0, 'BC': 0, 'D': 1, 'DE': 1, 'H': 2, 'HL': 2, 'SP': 3
}

# Register pair for LDAX/STAX (only B and D valid)
REGPAIRS_LDAX = {
    'B': 0, 'BC': 0, 'D': 1, 'DE': 1
}

# Condition codes for jumps/calls/returns
CONDITIONS = {
    'NZ': 0, 'Z': 1, 'NC': 2, 'C': 3, 'PO': 4, 'PE': 5, 'P': 6, 'M': 7
}

# Instructions with no operands
NO_OPERAND = {
    'NOP':  0x00,
    'RLC':  0x07,
    'RRC':  0x0F,
    'RAL':  0x17,
    'RAR':  0x1F,
    'DAA':  0x27,
    'CMA':  0x2F,
    'STC':  0x37,
    'CMC':  0x3F,
    'HLT':  0x76,
    'RET':  0xC9,
    'PCHL': 0xE9,
    'SPHL': 0xF9,
    'XCHG': 0xEB,
    'XTHL': 0xE3,
    'DI':   0xF3,
    'EI':   0xFB,
}

# Conditional returns: RNZ, RZ, RNC, RC, RPO, RPE, RP, RM
# Base opcode is 0xC0, condition in bits 3-5
COND_RET_BASE = 0xC0

# Conditional jumps: JNZ, JZ, JNC, JC, JPO, JPE, JP, JM
# Base opcode is 0xC2, condition in bits 3-5
COND_JMP_BASE = 0xC2

# Conditional calls: CNZ, CZ, CNC, CC, CPO, CPE, CP, CM
# Base opcode is 0xC4, condition in bits 3-5
COND_CALL_BASE = 0xC4

# Unconditional JMP and CALL
JMP = 0xC3
CALL = 0xCD

# RST instruction (RST 0-7)
RST_BASE = 0xC7

# Single register operations
# INR r: 00rrr100, DCR r: 00rrr101
INR_BASE = 0x04
DCR_BASE = 0x05

# Register pair operations
# LXI rp, nn: 00rp0001
# DAD rp: 00rp1001
# INX rp: 00rp0011
# DCX rp: 00rp1011
LXI_BASE = 0x01
DAD_BASE = 0x09
INX_BASE = 0x03
DCX_BASE = 0x0B

# LDAX/STAX (B or D pair only)
# LDAX rp: 00rp1010
# STAX rp: 00rp0010
LDAX_BASE = 0x0A
STAX_BASE = 0x02

# PUSH/POP (B, D, H, PSW)
# PUSH rp: 11rp0101
# POP rp: 11rp0001
PUSH_BASE = 0xC5
POP_BASE = 0xC1

# MOV dst, src: 01dddsss
MOV_BASE = 0x40

# MVI r, n: 00rrr110
MVI_BASE = 0x06

# Arithmetic/logical with register
# ADD r: 10000rrr, ADC r: 10001rrr, SUB r: 10010rrr, SBB r: 10011rrr
# ANA r: 10100rrr, XRA r: 10101rrr, ORA r: 10110rrr, CMP r: 10111rrr
ALU_REG = {
    'ADD': 0x80, 'ADC': 0x88, 'SUB': 0x90, 'SBB': 0x98,
    'ANA': 0xA0, 'XRA': 0xA8, 'ORA': 0xB0, 'CMP': 0xB8
}

# Arithmetic/logical immediate
# ADI n: 0xC6, ACI n: 0xCE, SUI n: 0xD6, SBI n: 0xDE
# ANI n: 0xE6, XRI n: 0xEE, ORI n: 0xF6, CPI n: 0xFE
ALU_IMM = {
    'ADI': 0xC6, 'ACI': 0xCE, 'SUI': 0xD6, 'SBI': 0xDE,
    'ANI': 0xE6, 'XRI': 0xEE, 'ORI': 0xF6, 'CPI': 0xFE
}

# Memory reference with 16-bit address
# LDA addr: 0x3A, STA addr: 0x32
# LHLD addr: 0x2A, SHLD addr: 0x22
LDA = 0x3A
STA = 0x32
LHLD = 0x2A
SHLD = 0x22

# I/O instructions
# IN port: 0xDB, OUT port: 0xD3
IN = 0xDB
OUT = 0xD3


def encode_no_operand(mnemonic):
    """Encode instruction with no operands."""
    return bytes([NO_OPERAND[mnemonic.upper()]])


def encode_mov(dst, src):
    """Encode MOV dst, src instruction."""
    dst_code = REGS[dst.upper()]
    src_code = REGS[src.upper()]
    return bytes([MOV_BASE | (dst_code << 3) | src_code])


def encode_mvi(reg, value):
    """Encode MVI reg, value instruction."""
    reg_code = REGS[reg.upper()]
    return bytes([MVI_BASE | (reg_code << 3), value & 0xFF])


def encode_lxi(regpair, value):
    """Encode LXI regpair, value instruction."""
    rp_code = REGPAIRS[regpair.upper()]
    return bytes([LXI_BASE | (rp_code << 4), value & 0xFF, (value >> 8) & 0xFF])


def encode_inr(reg):
    """Encode INR reg instruction."""
    reg_code = REGS[reg.upper()]
    return bytes([INR_BASE | (reg_code << 3)])


def encode_dcr(reg):
    """Encode DCR reg instruction."""
    reg_code = REGS[reg.upper()]
    return bytes([DCR_BASE | (reg_code << 3)])


def encode_inx(regpair):
    """Encode INX regpair instruction."""
    rp_code = REGPAIRS[regpair.upper()]
    return bytes([INX_BASE | (rp_code << 4)])


def encode_dcx(regpair):
    """Encode DCX regpair instruction."""
    rp_code = REGPAIRS[regpair.upper()]
    return bytes([DCX_BASE | (rp_code << 4)])


def encode_dad(regpair):
    """Encode DAD regpair instruction."""
    rp_code = REGPAIRS[regpair.upper()]
    return bytes([DAD_BASE | (rp_code << 4)])


def encode_ldax(regpair):
    """Encode LDAX regpair instruction (B or D only)."""
    rp_code = REGPAIRS_LDAX[regpair.upper()]
    return bytes([LDAX_BASE | (rp_code << 4)])


def encode_stax(regpair):
    """Encode STAX regpair instruction (B or D only)."""
    rp_code = REGPAIRS_LDAX[regpair.upper()]
    return bytes([STAX_BASE | (rp_code << 4)])


def encode_push(regpair):
    """Encode PUSH regpair instruction."""
    rp_code = REGPAIRS_PUSHPOP[regpair.upper()]
    return bytes([PUSH_BASE | (rp_code << 4)])


def encode_pop(regpair):
    """Encode POP regpair instruction."""
    rp_code = REGPAIRS_PUSHPOP[regpair.upper()]
    return bytes([POP_BASE | (rp_code << 4)])


def encode_alu_reg(mnemonic, reg):
    """Encode ALU operation with register (ADD, ADC, SUB, etc.)."""
    base = ALU_REG[mnemonic.upper()]
    reg_code = REGS[reg.upper()]
    return bytes([base | reg_code])


def encode_alu_imm(mnemonic, value):
    """Encode ALU immediate operation (ADI, ACI, SUI, etc.)."""
    opcode = ALU_IMM[mnemonic.upper()]
    return bytes([opcode, value & 0xFF])


def encode_jmp(addr):
    """Encode unconditional JMP."""
    return bytes([JMP, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_cond_jmp(cond, addr):
    """Encode conditional jump (JNZ, JZ, etc.)."""
    cond_code = CONDITIONS[cond.upper()]
    opcode = COND_JMP_BASE | (cond_code << 3)
    return bytes([opcode, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_call(addr):
    """Encode unconditional CALL."""
    return bytes([CALL, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_cond_call(cond, addr):
    """Encode conditional call (CNZ, CZ, etc.)."""
    cond_code = CONDITIONS[cond.upper()]
    opcode = COND_CALL_BASE | (cond_code << 3)
    return bytes([opcode, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_cond_ret(cond):
    """Encode conditional return (RNZ, RZ, etc.)."""
    cond_code = CONDITIONS[cond.upper()]
    return bytes([COND_RET_BASE | (cond_code << 3)])


def encode_rst(n):
    """Encode RST n instruction (n = 0-7)."""
    return bytes([RST_BASE | ((n & 7) << 3)])


def encode_lda(addr):
    """Encode LDA addr."""
    return bytes([LDA, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_sta(addr):
    """Encode STA addr."""
    return bytes([STA, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_lhld(addr):
    """Encode LHLD addr."""
    return bytes([LHLD, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_shld(addr):
    """Encode SHLD addr."""
    return bytes([SHLD, addr & 0xFF, (addr >> 8) & 0xFF])


def encode_in(port):
    """Encode IN port."""
    return bytes([IN, port & 0xFF])


def encode_out(port):
    """Encode OUT port."""
    return bytes([OUT, port & 0xFF])


# Conditional jump mnemonics
COND_JUMPS = {'JNZ', 'JZ', 'JNC', 'JC', 'JPO', 'JPE', 'JP', 'JM'}

# Conditional call mnemonics
COND_CALLS = {'CNZ', 'CZ', 'CNC', 'CC', 'CPO', 'CPE', 'CP', 'CM'}

# Conditional return mnemonics
COND_RETS = {'RNZ', 'RZ', 'RNC', 'RC', 'RPO', 'RPE', 'RP', 'RM'}


def get_cond_from_mnemonic(mnemonic):
    """Extract condition code from mnemonic like JNZ -> NZ."""
    m = mnemonic.upper()
    if m.startswith('J'):
        return m[1:]
    elif m.startswith('C') and m != 'CALL' and m != 'CMP' and m != 'CMA' and m != 'CMC':
        return m[1:]
    elif m.startswith('R') and m != 'RET' and m != 'RLC' and m != 'RRC' and m != 'RAL' and m != 'RAR' and m != 'RST':
        return m[1:]
    return None
