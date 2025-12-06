#!/usr/bin/env python3
"""
Clean up OCR'd 8080 assembly listing file.
Validates addresses, opcodes, and label references.
Multi-pass approach for thorough cleanup.
"""

import re
import sys
from typing import Optional, Tuple, List

# 8080 opcode table: mnemonic -> (opcode_byte, size)
OPCODES = {
    'NOP': (0x00, 1), 'HLT': (0x76, 1),
    'LDA': (0x3A, 3), 'STA': (0x32, 3),
    'LHLD': (0x2A, 3), 'SHLD': (0x22, 3),
    'XCHG': (0xEB, 1), 'XTHL': (0xE3, 1),
    'SPHL': (0xF9, 1), 'PCHL': (0xE9, 1),
    'ADI': (0xC6, 2), 'ACI': (0xCE, 2),
    'SUI': (0xD6, 2), 'SBI': (0xDE, 2),
    'DAA': (0x27, 1),
    'ANI': (0xE6, 2), 'ORI': (0xF6, 2),
    'XRI': (0xEE, 2), 'CPI': (0xFE, 2),
    'CMA': (0x2F, 1), 'CMC': (0x3F, 1), 'STC': (0x37, 1),
    'RLC': (0x07, 1), 'RRC': (0x0F, 1),
    'RAL': (0x17, 1), 'RAR': (0x1F, 1),
    'JMP': (0xC3, 3), 'JNZ': (0xC2, 3), 'JZ': (0xCA, 3),
    'JNC': (0xD2, 3), 'JC': (0xDA, 3),
    'JPO': (0xE2, 3), 'JPE': (0xEA, 3),
    'JP': (0xF2, 3), 'JM': (0xFA, 3),
    'CALL': (0xCD, 3), 'CNZ': (0xC4, 3), 'CZ': (0xCC, 3),
    'CNC': (0xD4, 3), 'CC': (0xDC, 3),
    'CPO': (0xE4, 3), 'CPE': (0xEC, 3),
    'CP': (0xF4, 3), 'CM': (0xFC, 3),
    'RET': (0xC9, 1), 'RNZ': (0xC0, 1), 'RZ': (0xC8, 1),
    'RNC': (0xD0, 1), 'RC': (0xD8, 1),
    'RPO': (0xE0, 1), 'RPE': (0xE8, 1),
    'RP': (0xF0, 1), 'RM': (0xF8, 1),
    'IN': (0xDB, 2), 'OUT': (0xD3, 2),
    'EI': (0xFB, 1), 'DI': (0xF3, 1),
}

REGS = {'B': 0, 'C': 1, 'D': 2, 'E': 3, 'H': 4, 'L': 5, 'M': 6, 'A': 7}
REG_PAIRS = {'B': 0, 'BC': 0, 'D': 1, 'DE': 1, 'H': 2, 'HL': 2, 'SP': 3, 'PSW': 3}


def fix_ocr_hex(s: str) -> str:
    """Fix common OCR errors in hex strings."""
    result = []
    s = s.upper()
    for c in s:
        if c == 'O':
            result.append('0')
        elif c == 'I' or c == 'l':
            result.append('1')
        elif c == 'Q':
            result.append('0')
        elif c == 'G':
            result.append('6')
        elif c == 'Z':
            result.append('2')
        elif c == '€':
            result.append('C')
        elif c == 'S':
            result.append('5')
        elif c == '£':
            result.append('E')
        else:
            result.append(c)
    return ''.join(result)


def fix_ocr_line(line: str) -> str:
    """Fix common OCR errors in the entire line."""
    # Fix € -> C in hex context
    line = re.sub(r'€([0-9A-Fa-f])', r'C\1', line)
    line = re.sub(r'([0-9A-Fa-f])€', r'\1C', line)

    # Fix 'go' at start -> '0' (OCR reading 0 as 'go' or 'o')
    # go00Cc -> 000C (handle duplicated trailing letter)
    # 'go' represents a single '0' that got misread
    line = re.sub(r'^go([0-9A-Fa-f]{2})([A-Fa-f])([a-f])\s', r'0\g<1>\2 ', line)
    line = re.sub(r'^go([0-9A-Fa-f]{2}[A-Fa-f]?)\s', r'0\1 ', line)
    line = re.sub(r'^on([0-9A-Fa-f]{2})', r'00\1', line)  # on -> 00

    # Fix common character confusions at line start (addresses)
    # Replace O/Q/o at start of 4-char hex address with 0
    line = re.sub(r'^([OQo])([0-9A-Fa-f]{3})\s', r'0\2 ', line)
    line = re.sub(r'^([0-9A-Fa-f])([OQo])([0-9A-Fa-f]{2})\s', r'\g<1>0\3 ', line)
    line = re.sub(r'^([0-9A-Fa-f]{2})([OQo])([0-9A-Fa-f])\s', r'\g<1>0\3 ', line)
    line = re.sub(r'^([0-9A-Fa-f]{3})([OQo])\s', r'\g<1>0 ', line)

    # Fix duplicated letters in addresses like 001Cc -> 001C, 00CCc -> 00C, 0000Cc -> 000C
    line = re.sub(r'^([0-9A-Fa-f]{3})([A-Fa-f])([a-f])\s', r'\g<1>\2 ', line)
    line = re.sub(r'^([0-9A-Fa-f]{2})([A-Fa-f])([A-Fa-f])([a-f])\s', r'\g<1>\2\3 ', line)
    # 0000Cc -> 000C (extra 0)
    line = re.sub(r'^([0-9A-Fa-f]{4})([A-Fa-f])([a-f])\s', r'\g<1> ', line)  # Truncate to 4 chars

    # Fix Di -> D1 (lowercase i should be 1)
    # Only in hex context at start of line after address
    line = re.sub(r'^([0-9A-Fa-f]{4}\s+)([0-9A-Fa-f])i\b', r'\g<1>\g<2>1', line)

    return line


# Common OCR mnemonic corrections
MNEMONIC_FIXES = {
    'LDA': 'LDA', 'IDA': 'LDA',  # I->L
    'IZ': 'JZ', 'INZ': 'JNZ', 'INC': 'JNC', 'IC': 'JC',
    'IM': 'JM', 'IP': 'JP', 'IPE': 'JPE', 'IPO': 'JPO',
    'IMP': 'JMP', 'IAC': 'JNC', 'JAC': 'JNC',  # JAC likely JNC
    'CALI': 'CALL', 'CAIL': 'CALL',
    'TNX': 'INX',  # T->I confusion
    'OW': 'DW',  # O->D
}


def parse_hex(s: str) -> Optional[int]:
    """Parse hex string, handling OCR errors."""
    s = fix_ocr_hex(s.strip())
    try:
        return int(s, 16)
    except:
        return None


def get_opcode_for_mnemonic(mnemonic: str, operands: str) -> Optional[int]:
    """Get expected opcode byte for a mnemonic and operands."""
    mnem = mnemonic.upper()
    ops = operands.upper().replace(' ', '').split(',') if operands else []

    if mnem in OPCODES:
        return OPCODES[mnem][0]

    # Register-based opcodes
    if mnem == 'MOV' and len(ops) == 2:
        d = REGS.get(ops[0].replace('.', ''), 0)
        s = REGS.get(ops[1].replace('.', ''), 0)
        return 0x40 | (d << 3) | s
    if mnem == 'MVI' and len(ops) >= 1:
        d = REGS.get(ops[0], 0)
        return 0x06 | (d << 3)
    if mnem == 'LXI' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x01 | (rp << 4)
    if mnem == 'LDAX' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x0A | (rp << 4)
    if mnem == 'STAX' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x02 | (rp << 4)
    if mnem == 'PUSH' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0xC5 | (rp << 4)
    if mnem == 'POP' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0xC1 | (rp << 4)
    if mnem == 'INX' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x03 | (rp << 4)
    if mnem == 'DCX' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x0B | (rp << 4)
    if mnem == 'DAD' and len(ops) >= 1:
        rp = REG_PAIRS.get(ops[0], 0)
        return 0x09 | (rp << 4)
    if mnem == 'INR' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x04 | (r << 3)
    if mnem == 'DCR' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x05 | (r << 3)
    if mnem == 'ADD' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x80 | r
    if mnem == 'ADC' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x88 | r
    if mnem == 'SUB' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x90 | r
    if mnem == 'SBB' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0x98 | r
    if mnem == 'ANA' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0xA0 | r
    if mnem == 'XRA' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0xA8 | r
    if mnem == 'ORA' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0xB0 | r
    if mnem == 'CMP' and len(ops) >= 1:
        r = REGS.get(ops[0], 0)
        return 0xB8 | r
    if mnem == 'RST' and len(ops) >= 1:
        try:
            n = int(ops[0])
            return 0xC7 | (n << 3)
        except:
            pass

    return None


def get_mnemonic_for_opcode(opcode: int) -> Optional[str]:
    """Get mnemonic for an opcode byte."""
    for mnem, (opc, size) in OPCODES.items():
        if opc == opcode:
            return mnem

    # Register-based opcodes
    if opcode == 0x76:
        return 'HLT'
    if (opcode & 0xC0) == 0x40:
        return 'MOV'
    if (opcode & 0xC7) == 0x06:
        return 'MVI'
    if (opcode & 0xCF) == 0x01:
        return 'LXI'
    if (opcode & 0xEF) == 0x0A:
        return 'LDAX'
    if (opcode & 0xEF) == 0x02:
        return 'STAX'
    if (opcode & 0xCF) == 0xC5:
        return 'PUSH'
    if (opcode & 0xCF) == 0xC1:
        return 'POP'
    if (opcode & 0xCF) == 0x03:
        return 'INX'
    if (opcode & 0xCF) == 0x0B:
        return 'DCX'
    if (opcode & 0xCF) == 0x09:
        return 'DAD'
    if (opcode & 0xC7) == 0x04:
        return 'INR'
    if (opcode & 0xC7) == 0x05:
        return 'DCR'
    if (opcode & 0xF8) == 0x80:
        return 'ADD'
    if (opcode & 0xF8) == 0x88:
        return 'ADC'
    if (opcode & 0xF8) == 0x90:
        return 'SUB'
    if (opcode & 0xF8) == 0x98:
        return 'SBB'
    if (opcode & 0xF8) == 0xA0:
        return 'ANA'
    if (opcode & 0xF8) == 0xA8:
        return 'XRA'
    if (opcode & 0xF8) == 0xB0:
        return 'ORA'
    if (opcode & 0xF8) == 0xB8:
        return 'CMP'
    if (opcode & 0xC7) == 0xC7:
        return 'RST'

    return None


def get_instruction_size(opcode: int) -> int:
    """Get instruction size from opcode byte."""
    mnem = get_mnemonic_for_opcode(opcode)
    if mnem is None:
        return 1

    if mnem in OPCODES:
        return OPCODES[mnem][1]

    # Single byte register ops
    if mnem in ('MOV', 'ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP',
                'LDAX', 'STAX', 'PUSH', 'POP', 'INX', 'DCX', 'DAD', 'INR', 'DCR', 'RST'):
        return 1
    if mnem == 'MVI':
        return 2
    if mnem == 'LXI':
        return 3

    return 1


def infer_operand_from_opcode(opcode: int, mnemonic: str) -> str:
    """Infer the register operand from the opcode byte."""
    mnem = mnemonic.upper()
    reg_names = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
    rp_names = ['B', 'D', 'H', 'SP']
    rp_names_push = ['B', 'D', 'H', 'PSW']

    if mnem == 'MOV':
        d = (opcode >> 3) & 7
        s = opcode & 7
        return f"{reg_names[d]},{reg_names[s]}"
    if mnem == 'MVI':
        d = (opcode >> 3) & 7
        return f"{reg_names[d]}"
    if mnem == 'LXI':
        rp = (opcode >> 4) & 3
        return rp_names[rp]
    if mnem in ('LDAX', 'STAX'):
        rp = (opcode >> 4) & 1
        return rp_names[rp]
    if mnem in ('PUSH', 'POP'):
        rp = (opcode >> 4) & 3
        return rp_names_push[rp]
    if mnem in ('INX', 'DCX', 'DAD'):
        rp = (opcode >> 4) & 3
        return rp_names[rp]
    if mnem in ('INR', 'DCR'):
        r = (opcode >> 3) & 7
        return reg_names[r]
    if mnem in ('ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP'):
        r = opcode & 7
        return reg_names[r]
    if mnem == 'RST':
        n = (opcode >> 3) & 7
        return str(n)

    return ''


class ListingCleaner:
    def __init__(self):
        self.labels = {}  # label -> address
        self.warnings = []
        self.fixes = []

    def clean_instruction_line(self, line_num: int, line: str) -> str:
        """Clean up an instruction line."""
        # Try to parse: ADDR HEXBYTES MNEMONIC [OPERANDS] [;COMMENT]
        # Allow for various OCR corruptions

        # First, fix obvious OCR issues
        line = fix_ocr_line(line)

        # Match pattern: 4 hex chars, space, 2-6 hex chars (including OCR errors), space, word, rest
        # Include common OCR errors in hex: O,o,Q,q (->0), S,s (->5), G,g (->6), I,l (->1), €,£ (->C,E)
        m = re.match(r'^([0-9A-Fa-fOoQqSsGgIl]{4})\s+([0-9A-Fa-fOoQqSsGgIl€£]{2,6})\s+(\S+)\s*(.*)', line)
        if not m:
            return line

        addr_str, hex_str, mnemonic, rest = m.groups()

        # Fix address
        addr_fixed = fix_ocr_hex(addr_str)

        # Fix hex bytes - may have extra characters due to OCR
        hex_fixed = fix_ocr_hex(hex_str)
        # Validate hex length (must be 2, 4, or 6)
        # Will be refined later based on instruction size

        # Parse operands and comment
        # The rest might have comment merged in without semicolon
        operands = ''
        comment = ''

        # Split on semicolon if present
        # Note: OCR sometimes corrupts ; to s; or other chars
        if ';' in rest:
            parts = rest.split(';', 1)
            operands = parts[0].strip()
            # Remove trailing OCR-corrupted comment markers like 's' before ';'
            if operands and operands[-1].lower() == 's' and len(operands) > 1 and operands[-2] in ' \t':
                operands = operands[:-1].strip()
            comment = ';' + parts[1]
        else:
            # Check if there's text after the operand that looks like a comment
            # Heuristic: register operands are single letters or short
            parts = rest.split()
            if parts:
                # First part is likely operand
                operands = parts[0]
                # If there are more parts, might be comment without semicolon
                if len(parts) > 1:
                    # Check if first part looks like a valid operand
                    first = parts[0].upper().replace(',', '')
                    if first in REGS or first in REG_PAIRS or len(first) <= 3:
                        # Rest is probably comment
                        comment = ';' + ' '.join(parts[1:])
                    else:
                        # First part might not be operand - use all
                        operands = rest

        operands = operands.strip()

        # Apply mnemonic fixes first
        mnem_upper = mnemonic.upper()
        if mnem_upper in MNEMONIC_FIXES:
            mnem_upper = MNEMONIC_FIXES[mnem_upper]

        # Validate and potentially fix based on opcode
        opcode = parse_hex(hex_fixed[:2]) if len(hex_fixed) >= 2 else None

        # Get expected opcode from mnemonic
        expected_opcode = get_opcode_for_mnemonic(mnem_upper, operands)

        # Verify the actual opcode is valid
        actual_mnem = get_mnemonic_for_opcode(opcode) if opcode is not None else None

        if expected_opcode is not None:
            expected_hex_str = f"{expected_opcode:02X}"
            if opcode is None or hex_fixed[:2] != expected_hex_str:
                # Check if actual opcode is same mnemonic but different register
                # In that case, trust the hex byte (operand might be OCR-corrupted)
                if actual_mnem and actual_mnem.upper() == mnem_upper:
                    # Same mnemonic, different register - trust hex byte
                    # Infer the correct operand from opcode
                    pass
                else:
                    # Different mnemonic entirely - fix the hex to match mnemonic
                    self.warnings.append(f"Line {line_num}: Fixed opcode {hex_fixed[:2]} -> {expected_hex_str} for {mnem_upper}")
                    hex_fixed = expected_hex_str + hex_fixed[2:]
                    opcode = expected_opcode

        # Fix hex length based on instruction size
        if opcode is not None:
            expected_size = get_instruction_size(opcode)
            expected_hex_len = expected_size * 2
            if len(hex_fixed) != expected_hex_len:
                if len(hex_fixed) > expected_hex_len:
                    # Trim extra characters
                    hex_fixed = hex_fixed[:expected_hex_len]
                elif len(hex_fixed) < expected_hex_len:
                    # Pad with zeros (might be wrong but better than odd length)
                    hex_fixed = hex_fixed.ljust(expected_hex_len, '0')

        # Reconstruct the line - already fixed mnemonic above
        mnem_fixed = mnem_upper
        if mnem_fixed in MNEMONIC_FIXES:
            mnem_fixed = MNEMONIC_FIXES[mnem_fixed]

        # Format with proper spacing
        result = f"{addr_fixed} {hex_fixed:<6s}  {mnem_fixed}"
        if operands:
            result += f"\t{operands}"
        if comment:
            result += f"\t{comment}"

        return result

    def clean_equ_line(self, line_num: int, line: str) -> str:
        """Clean up an EQU line."""
        line = fix_ocr_line(line)

        m = re.match(r'^([0-9A-Fa-fOoQq]{4})\s+([0-9A-Fa-fOoQq]{4})\s+(\S+)\s+EQU\s+(.*)', line, re.IGNORECASE)
        if not m:
            return line

        addr_str, value_str, label, expr = m.groups()
        addr_fixed = fix_ocr_hex(addr_str)
        value_fixed = fix_ocr_hex(value_str)

        # Record label
        value = parse_hex(value_fixed)
        if value is not None:
            self.labels[label.upper()] = value

        return f"{addr_fixed} {value_fixed}   {label}\tEQU\t{expr.strip()}"

    def clean_data_line(self, line_num: int, line: str) -> str:
        """Clean up a DB/DW line."""
        line = fix_ocr_line(line)

        # Match: ADDR HEXBYTES DB/DW/BB/OB rest
        m = re.match(r'^([0-9A-Fa-fOoQq]{4})\s+([0-9A-Fa-fOoQq]{2,8})\s+(DB|DW|BB|OB)\s+(.*)', line, re.IGNORECASE)
        if not m:
            return line

        addr_str, hex_str, directive, rest = m.groups()
        addr_fixed = fix_ocr_hex(addr_str)
        hex_fixed = fix_ocr_hex(hex_str)

        # Fix directive OCR errors
        dir_fixed = 'DB' if directive.upper() in ('DB', 'BB', 'OB') else 'DW'

        return f"{addr_fixed} {hex_fixed:<6s}  {dir_fixed}\t{rest.strip()}"

    def process_file(self, input_path: str, output_path: str):
        """Process the file."""
        with open(input_path, 'r') as f:
            lines = f.readlines()

        output_lines = []

        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()

            # Always apply OCR fixes first
            line = fix_ocr_line(line)

            # Skip empty lines and headers
            if not line.strip():
                output_lines.append(line)
                continue

            if line.startswith('===') or 'basIC.LST' in line or 'basIC.tST' in line or 'basIC,.LST' in line:
                output_lines.append(line)
                continue

            # Pure comment lines
            if line.strip().startswith(';'):
                output_lines.append(line)
                continue

            # Label-only lines
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*:\s*$', line):
                output_lines.append(line)
                continue

            # Check for EQU
            if re.search(r'\bEQU\b', line, re.IGNORECASE):
                output_lines.append(self.clean_equ_line(line_num, line))
                continue

            # Check for DB/DW
            if re.search(r'\b(DB|DW|BB|OB)\b', line, re.IGNORECASE):
                # Make sure it's a data line not instruction
                if re.match(r'^[0-9A-Fa-fOoQqSsGgIl]{4}\s+[0-9A-Fa-fOoQqSsGgIl]+\s+(DB|DW|BB|OB)', line, re.IGNORECASE):
                    output_lines.append(self.clean_data_line(line_num, line))
                    continue

            # Try to parse as instruction
            if re.match(r'^[0-9A-Fa-fOoQqSsGgIl]{4}\s+[0-9A-Fa-fOoQqSsGgIl€£]+\s+\S', line):
                output_lines.append(self.clean_instruction_line(line_num, line))
                continue

            # Pass through unchanged
            output_lines.append(line)

        # Write output
        with open(output_path, 'w') as f:
            for line in output_lines:
                f.write(line + '\n')

        print(f"Processed {len(lines)} lines")
        print(f"Found {len(self.labels)} labels")
        print(f"Found {len(self.warnings)} warnings")
        for w in self.warnings[:50]:
            print(f"  {w}")
        if len(self.warnings) > 50:
            print(f"  ... and {len(self.warnings) - 50} more")
        print(f"\nWrote {len(output_lines)} lines to {output_path}")


if __name__ == '__main__':
    input_file = 'AltairBASIC-1975-v0.txt'
    output_file = 'AltairBASIC-1975-v1.txt'

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    cleaner = ListingCleaner()
    cleaner.process_file(input_file, output_file)
