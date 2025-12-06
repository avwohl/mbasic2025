#!/usr/bin/env python3
"""
Second pass cleanup for OCR'd 8080 assembly listing.
Fixes remaining issues after first pass - conservative approach.
"""

import re
import sys


def fix_comment_marker(line: str) -> str:
    """Fix : used as ; for comments."""
    # Pattern: after operand, tab, then : followed by text
    # Only fix if it looks like a comment (: followed by letter or space+letter)
    line = re.sub(r'(\t):([A-Za-z ])', r'\1;\2', line)

    # Fix double semicolons
    line = re.sub(r';;+', r';', line)

    # Fix ;: -> ;
    line = re.sub(r';:', r';', line)

    # Fix trailing : that should be ; at end of line
    line = re.sub(r'\t:$', r'\t;', line)

    # Fix common OCR errors where s or 5 should be ; before comment
    # Pattern: operand followed by spaces and then s or 5 followed by lowercase word
    line = re.sub(r'(\t\S+)\s{2,}s([a-z])', r'\1\t;\2', line)
    line = re.sub(r'(\t\S+)\s{2,}5([a-z])', r'\1\t;\2', line)

    # Fix i at start of comment that should be ;
    line = re.sub(r'(\t\S+)\s{2,}i([a-z])', r'\1\t;\2', line)

    # Fix EQU lines with trailing comments (no semicolon)
    # Pattern: EQU value followed by spaces and uppercase text
    line = re.sub(r'(EQU\s+[0-9A-Fa-f]+H?)\s{2,}([A-Z][A-Z ])', r'\1\t;\2', line)

    # Fix lines that are just uppercase text (should be comments)
    # Pattern: tab followed by uppercase words (like "STATEMENT ROUTINES")
    m = re.match(r'^\t([A-Z][A-Z ]+[A-Z])\s*$', line)
    if m:
        line = '; ' + m.group(1)

    # Fix lines starting with spaces followed by uppercase text (section comments)
    # Pattern: 2+ spaces followed by UPPERCASE text ending with non-alpha
    m = re.match(r'^  +([A-Z][A-Z ]+[A-Z])[^A-Za-z]*$', line)
    if m:
        line = '; ' + m.group(1)

    return line


def fix_garbage_chars(line: str) -> str:
    """Fix various garbage characters."""
    # Fix ¢ -> c in text
    line = line.replace('¢', 'c')
    # Fix em-dash to regular dash
    line = line.replace('—', '-')
    # Fix Unicode smart quotes to ASCII
    line = line.replace('\u2018', "'")  # LEFT SINGLE QUOTATION MARK
    line = line.replace('\u2019', "'")  # RIGHT SINGLE QUOTATION MARK
    line = line.replace('\u201c', '"')  # LEFT DOUBLE QUOTATION MARK
    line = line.replace('\u201d', '"')  # RIGHT DOUBLE QUOTATION MARK
    # Fix tilde to dash in expressions like KEYINS~80H -> KEYINS-80H
    line = re.sub(r'([A-Z]+)~(80H)', r'\1-\2', line)
    # Fix specific heavily corrupted mnemonic
    line = line.replace('~©§=«-.AZ', 'JZ')
    # Fix £ -> E in operands (MVI £ -> MVI E)
    line = re.sub(r'\tMVI\t£', r'\tMVI\tE', line)
    # Fix £ -> E in hex data
    line = line.replace('£', 'E')
    # Remove garbage characters (replacement chars, etc)
    line = re.sub(r'[\ufffd]+', '', line)  # Unicode replacement char
    line = re.sub(r'�+', '', line)  # Displayed as question mark boxes
    # Fix underscore garbage before quotes
    line = re.sub(r'_\s*"', '"', line)
    # Remove any remaining high-bit garbage before quotes in DB lines
    line = re.sub(r'DB\t"', 'DB\t"', line)  # Normalize
    return line


def fix_ocr_values(line: str) -> str:
    """Fix OCR errors in EQU values and hex constants."""
    # Fix CEQU -> EQU
    line = re.sub(r'\bCEQU\b', 'EQU', line)

    # Fix specific EQU line patterns where address has O errors
    # Pattern: OO04E O0BD -> 004E 00BD
    m = re.match(r'^OO([0-9A-F]{2,3}) O([0-9A-F]{2,3})\s+(\S+)\s+EQU', line)
    if m:
        addr = '00' + m.group(1)[-2:]
        val = '0' + m.group(2)
        rest = line[len(m.group(0))-3:]  # Keep "EQU" onward
        line = addr + ' ' + val + ' ' + m.group(3) + ' EQU' + rest

    # Fix EQUEQU -> EQU (doubled)
    line = re.sub(r'\bEQUEQU\b', 'EQU', line)

    # Fix 0O -> 00 in hex values
    line = re.sub(r'\b0O([0-9A-F]{2})H\b', r'00\1H', line)
    line = re.sub(r'\b0O00H\b', r'0000H', line)

    # Fix O -> 0 in hex values like ODH, OAH, OFH, OSH
    # Pattern: O followed by hex digit and H
    line = re.sub(r'\bO([0-9A-F])H\b', r'0\1H', line)
    line = re.sub(r'\bO([0-9A-F]{2})H\b', r'0\1H', line)

    # Fix trailing . that should be ; for comment
    line = re.sub(r'\s+\.\s*$', '', line)  # Remove trailing . for now
    line = re.sub(r'\s{2,}\.\s*$', '', line)

    # Fix trailing : or ~ or = after EQU expressions (OCR garbage)
    line = re.sub(r'(EQU\s+\S+)\s+[:~=]\s*$', r'\1', line)
    line = re.sub(r'(EQU\s+\S+\+\d+)\s+[:~=]\s*$', r'\1', line)
    # Fix = before ; in EQU lines (garbage before comment)
    line = re.sub(r'(EQU\s+\S+)\s+=\s*(;)', r'\1\t\2', line)

    # Fix OcSH -> 0C9H (lowercase c, missing 9)
    line = re.sub(r'\bOcSH\b', '0C9H', line)
    line = re.sub(r'\bOc9H\b', '0C9H', line)

    # Fix EQU with value followed by text (missing semicolon before comment)
    # Pattern: EQU value    TEXT -> EQU value ;TEXT
    line = re.sub(r'(EQU\s+[0-9A-Fa-fHh]+)\s{2,}([A-Z][A-Z])', r'\1\t;\2', line)

    # Fix trailing : after DW expressions
    line = re.sub(r'(DW\s+\S+)\s+:\s*$', r'\1', line)

    # Fix label; -> label: (semicolon instead of colon after label name)
    m = re.match(r'^([A-Za-z][A-Za-z0-9]*);$', line)
    if m:
        line = m.group(1) + ':'

    # Fix ''T+128 -> 'T'+128 (double quote OCR error)
    line = re.sub(r"''([A-Za-z])\+128", r"'\1'+128", line)

    # Fix 'X+128 -> 'X'+128 (missing closing quote)
    line = re.sub(r"'([A-Za-z0-9$<>?])\+128", r"'\1'+128", line)

    # Fix single-char operators missing closing quote
    # '++128 -> '+'+128, '-+128 -> '-'+128, etc.
    line = re.sub(r"'([+\-*/\\<>=])\+128", r"'\1'+128", line)

    # Fix '$4+128 -> '$'+128 (4 is garbage)
    line = re.sub(r"'([\$\?\*\+\-/\\<>=])4\+128", r"'\1'+128", line)

    # Fix '(+... patterns - KEYS-'( -> KEYS-'('
    line = re.sub(r"'(\()\s*;", r"'\1'\t;", line)

    # Fix 'Xx+128 -> 'X'+128 (extra char before +128)
    line = re.sub(r"'([A-Za-z])[a-z]\+128", r"'\1'+128", line)

    # Fix '''T' -> 'T' (triple quote)
    line = re.sub(r"'''([A-Za-z])'", r"'\1'", line)

    # Fix OB -> DB (O misread as D)
    line = re.sub(r'^\tOB\s', '\tDB\t', line)
    # Also in listing context
    line = re.sub(r'\sOB\s+KEY', '\tDB\tKEY', line)
    line = re.sub(r'\sOB\t', '\tDB\t', line)

    # Fix DO -> DB (misread)
    line = re.sub(r'^\tDO\s', '\tDB\t', line)
    line = re.sub(r'\sDO\s+KEY', '\tDB\tKEY', line)

    # Fix specific corrupted DB lines for keywords
    # "FY, IN+128 -> "FN", 'N'+128
    line = re.sub(r'"FY, IN\+128', '"FN", \'N\'+128', line)
    # "$4+128 -> '$'+128
    line = re.sub(r'"\$4\+128', "'$'+128", line)
    # "44128 -> '^'+128
    line = re.sub(r'"44128', "'^'+128", line)
    # ""O", 'R'+128 -> "O", 'R'+128
    line = re.sub(r'""O", ', '"O", ', line)

    return line


def fix_address_ocr(line: str) -> str:
    """Fix OCR errors in addresses at start of line."""
    # First, handle addresses with dash (which makes them 5 chars)
    # Em-dashes have already been converted to regular dashes
    m = re.match(r'^([O0-9A-F£€]*)-([O0-9A-F£€]*)\s', line)
    if m:
        # Remove dash from address
        addr = m.group(1) + m.group(2)
        rest = line[len(m.group(0))-1:]  # keep trailing space
        if len(addr) == 4:
            line = addr + rest
        elif len(addr) == 3:
            # May need padding
            line = '0' + addr + rest

    # Handle lowercase i at start (should be 1)
    m = re.match(r'^i([0-9A-F]{3})\s', line)
    if m:
        line = '1' + m.group(1) + line[4:]

    # Handle § (section sign) -> S (but in address context likely 5)
    m = re.match(r'^§([0-9A-F]{3,4})\s', line)
    if m:
        line = '5' + m.group(1)[-3:] + line[len(m.group(0))-1:]

    # Handle Q -> 0 at start of address
    m = re.match(r'^Q([O0-9A-F]{3})\s', line)
    if m:
        line = '0' + m.group(1).replace('O', '0') + line[4:]

    # Handle G -> 0 at start of address (GO4E -> 004E)
    m = re.match(r'^G([O0-9A-F]{3})\s', line)
    if m:
        line = '0' + m.group(1).replace('O', '0') + line[4:]

    # Handle Gi -> 01 at start of address (GiOC -> 010C)
    m = re.match(r'^Gi([O0-9A-F]{2})\s', line)
    if m:
        line = '01' + m.group(1).replace('O', '0') + line[4:]

    # Handle OO -> 00 at start of address (OO4E -> 004E)
    m = re.match(r'^OO([0-9A-F]{2})\s', line)
    if m:
        line = '00' + m.group(1) + line[4:]

    # Handle OC/OD/OB/OE -> 0C/0D/0B/0E at start (OCS5F -> 0C5F, OB85E -> 0B5E, etc.)
    m = re.match(r'^O([BCDE])([A-Za-z0-9])([0-9A-F])([A-Za-z0-9])\s', line)
    if m:
        # Convert to proper hex - S/s->5, i->1
        d2 = m.group(2).upper()
        d4 = m.group(4).upper()
        if d2 == 'S':
            d2 = '5'
        if d2 == 'I':
            d2 = '1'
        if d4 == 'S':
            d4 = '5'
        if d4 == 'I':
            d4 = '1'
        if d4 == 'E':  # E at end might be legitimate
            pass
        line = '0' + m.group(1) + d2 + m.group(3) + d4 + line[5:]

    # Handle lowercase o -> 0 at start
    m = re.match(r'^o([A-F0-9])([0-9A-Fa-f])([0-9A-Fa-f])\s', line)
    if m:
        fixed = '0' + m.group(1) + m.group(2).upper() + m.group(3).upper()
        # Fix i->1, c->C
        fixed = fixed.replace('i', '1').replace('c', 'C')
        line = fixed + line[4:]

    # Handle OS -> 05 at start of address (OS5BE -> 055BE, but that's 5 chars so truncate)
    m = re.match(r'^OS([0-9A-F]{3})\s', line)
    if m:
        line = '05' + m.group(1)[1:] + line[5:]  # Takes last 2 chars of match

    # Handle more specific address OCR: o4cp -> 04C? with repair
    m = re.match(r'^o([0-9])([a-zA-Z])([a-zA-Z0-9])\s', line)
    if m:
        d1 = m.group(1)
        d2 = m.group(2).upper()
        d3 = m.group(3).upper()
        if d3 == 'P':
            d3 = 'F'  # P misread as F
        line = '0' + d1 + d2 + d3 + line[4:]

    # Handle QO -> 00 at start (QO6CA -> 006CA, truncate to 006C)
    m = re.match(r'^QO([0-9A-F]{3})\s', line)
    if m:
        line = '00' + m.group(1)[:2] + line[5:]

    # Handle O6GEF -> 06EF (G is garbage)
    m = re.match(r'^O([0-9])G([0-9A-F]{2})\s', line)
    if m:
        line = '0' + m.group(1) + m.group(2) + line[5:]

    # Handle 0c98s -> 0C98 (lowercase c, s garbage)
    m = re.match(r'^0([a-f])([0-9A-F]{2})([a-z])\s', line)
    if m:
        line = '0' + m.group(1).upper() + m.group(2) + line[5:]

    # Handle O4FO0 -> 04F0 (O -> 0)
    m = re.match(r'^O([0-9])F([O0])([0-9])\s', line)
    if m:
        line = '0' + m.group(1) + 'F' + m.group(2).replace('O', '0') + line[5:]

    # Handle O07A7 -> 07A7 (leading O extra)
    m = re.match(r'^O0([0-9A-F]{3})\s', line)
    if m:
        line = '0' + m.group(1) + line[5:]

    # Handle O8GE -> 08?E (G is garbage, probably a hex char like 2)
    m = re.match(r'^O([0-9])G([A-F])\s', line)
    if m:
        # G could be 0 or another digit, common case is 0
        line = '0' + m.group(1) + '0' + m.group(2) + line[4:]

    # Handle o9gco -> 09C0 (lowercase o->0, g->C)
    m = re.match(r'^o([0-9])g([a-z])([a-z0-9])\s', line)
    if m:
        d2 = m.group(2).upper()
        d3 = m.group(3).upper()
        if d2 == 'G':
            d2 = 'C'  # G looks like C
        if d3 == 'O':
            d3 = '0'
        line = '0' + m.group(1) + d2 + d3 + line[5:]

    # Handle osc4 -> 09C4 (s->9, lowercase)
    m = re.match(r'^os([a-z])([0-9])\s', line)
    if m:
        line = '09' + m.group(1).upper() + m.group(2) + line[4:]

    # Handle OQ9EC -> 09EC (Q->9)
    m = re.match(r'^OQ([0-9])([A-F])([0-9A-F])\s', line)
    if m:
        line = '0' + m.group(1) + m.group(2) + m.group(3) + line[5:]

    # Handle OSF2 -> 09F2 (S->9)
    m = re.match(r'^OS([A-F])([0-9])\s', line)
    if m:
        line = '09' + m.group(1) + m.group(2) + line[4:]

    # Handle GO5AF -> 05AF (G garbage)
    m = re.match(r'^GO([0-9])([A-F])([0-9A-F])\s', line)
    if m:
        line = '0' + m.group(1) + m.group(2) + m.group(3) + line[5:]

    # Handle OA9S7 -> 0A97 (S->9, extra digit)
    m = re.match(r'^OA([0-9])S([0-9])\s', line)
    if m:
        line = '0A' + m.group(1) + m.group(2) + line[5:]

    # Handle OAF9O -> 0AF90 -> 0AF9 (trailing O)
    m = re.match(r'^OAF([0-9])O\s', line)
    if m:
        line = '0AF' + m.group(1) + line[5:]

    # Handle oBDo -> 0BD0 (lowercase)
    m = re.match(r'^o([A-F])([A-F])o\s', line)
    if m:
        line = '0' + m.group(1) + m.group(2) + '0' + line[4:]

    # Handle oBDo with longer pattern
    m = re.match(r'^oB([A-F])([a-z0-9])\s', line)
    if m:
        d2 = m.group(2).upper()
        if d2 == 'O':
            d2 = '0'
        line = '0B' + m.group(1) + d2 + line[4:]

    # Handle ocsac -> 0C9AC -> 0C9A (c->C, s->9, extra char)
    m = re.match(r'^oc([a-z])([a-z])([a-z0-9])\s', line)
    if m:
        d1 = m.group(1).upper()
        d2 = m.group(2).upper()
        d3 = m.group(3).upper()
        if d1 == 'S':
            d1 = '9'  # S looks like 9
        if d2 == 'A':
            pass  # A is valid
        if d3 == 'C':
            pass  # extra C is valid, drop it
        line = '0C' + d1 + d2 + line[5:]

    # Handle ocDO -> 0CD0 (lowercase)
    m = re.match(r'^oc([A-F])([O0])\s', line)
    if m:
        line = '0C' + m.group(1) + m.group(2).replace('O', '0') + line[4:]

    # Handle OCES -> 0CE? (S->5 or other)
    m = re.match(r'^OCE([A-Z])\s', line)
    if m:
        d = m.group(1)
        if d == 'S':
            d = '5'
        line = '0CE' + d + line[4:]

    # Handle oD1ic -> 0D1? (lowercase, extra char)
    m = re.match(r'^oD([0-9])([a-z])([a-z])\s', line)
    if m:
        d2 = m.group(2).upper()
        if d2 == 'I':
            d2 = '1'
        line = '0D' + m.group(1) + d2 + line[5:]

    # Handle oDgCc -> 0D?C (g->9 or similar, extra c)
    m = re.match(r'^oD([a-z])([A-F])([a-z])\s', line)
    if m:
        d1 = m.group(1).upper()
        if d1 == 'G':
            d1 = '9'  # G looks like 9
        line = '0D' + d1 + m.group(2) + line[5:]

    # Handle ODBS5 -> 0DB5 (S->5)
    m = re.match(r'^ODB([A-Z])([0-9])\s', line)
    if m:
        d1 = m.group(1)
        if d1 == 'S':
            d1 = '5'
        line = '0DB' + d1 + line[5:]

    # Handle opc4 -> 0DC4 (lowercase, p->D)
    m = re.match(r'^op([a-z])([0-9])\s', line)
    if m:
        d1 = m.group(1).upper()
        if d1 == 'C':
            pass  # C is valid
        line = '0D' + d1 + m.group(2) + line[4:]

    # Handle OE5SE -> 0E5? (S->5, E extra)
    m = re.match(r'^OE([0-9])([A-Z])E\s', line)
    if m:
        d2 = m.group(2)
        if d2 == 'S':
            d2 = '5'
        line = '0E' + m.group(1) + d2 + line[5:]

    # Only process lines that look like they start with an address
    m = re.match(r'^([O0-9A-F£€]{4})\s', line)
    if not m:
        return line

    addr = m.group(1)
    fixed = addr
    # O -> 0
    fixed = fixed.replace('O', '0')
    # £ -> E
    fixed = fixed.replace('£', 'E')
    # € -> C
    fixed = fixed.replace('€', 'C')

    if fixed != addr:
        line = fixed + line[4:]
    return line


def fix_hex_bytes(line: str) -> str:
    """Fix OCR errors in hex bytes (after address)."""
    # Handle specific problematic hex patterns first
    # cO0C104 -> C00C104 is too long, probably C00C10
    m = re.match(r'^([0-9A-F]{4}) ([cC])([O0])([0-9A-F])([0-9A-F])([0-9])([0-9])([0-9]?)(\s)', line)
    if m:
        # Fix: cO0C104 is probably CD0C10 (CALL instruction)
        fixed = 'CD' + m.group(4) + m.group(5) + m.group(6) + m.group(7)
        if len(fixed) == 6:
            line = m.group(1) + ' ' + fixed + m.group(9) + line[len(m.group(0)):]
            return line

    # Handle DCO000 -> DC0000 (O->0)
    m = re.match(r'^([0-9A-F]{4}) DC([O0])([0-9A-F]{3})(\s)', line)
    if m:
        fixed = 'DC' + m.group(2).replace('O', '0') + m.group(3)
        line = m.group(1) + ' ' + fixed + m.group(4) + line[len(m.group(0)):]
        return line

    # Handle CbDO000 -> CD0000 (b->D, O->0)
    m = re.match(r'^([0-9A-F]{4}) C[bB]D([O0])([0-9A-F]{3})(\s)', line)
    if m:
        fixed = 'CD' + m.group(2).replace('O', '0') + m.group(3)
        line = m.group(1) + ' ' + fixed + m.group(4) + line[len(m.group(0)):]
        return line

    # Handle CPOC00 -> CP0C00 (O->0) or similar
    m = re.match(r'^([0-9A-F]{4}) CP([O0])([A-F])([0-9]{2})(\s)', line)
    if m:
        fixed = 'CP' + m.group(2).replace('O', '0') + m.group(3) + m.group(4)
        line = m.group(1) + ' ' + fixed + m.group(5) + line[len(m.group(0)):]
        return line

    # Handle p20000 -> D20000 (p->D for JNC opcode)
    m = re.match(r'^([0-9A-F]{4}) [pP]2([0-9A-F]{4})(\s)', line)
    if m:
        line = m.group(1) + ' D2' + m.group(2) + m.group(3) + line[len(m.group(0)):]
        return line

    # Handle CcDO0CO4 -> CD0C04 (c->D, O->0)
    m = re.match(r'^([0-9A-F]{4}) [Cc][cC]D([O0])([0-9])([A-F])([O0])([0-9])(\s)', line)
    if m:
        fixed = 'CD' + m.group(2).replace('O', '0') + m.group(3) + m.group(4) + m.group(5).replace('O', '0') + m.group(6)
        line = m.group(1) + ' ' + fixed + m.group(7) + line[len(m.group(0)):]
        return line

    # Handle AQ -> A7 (Q->7 for ANA A opcode)
    m = re.match(r'^([0-9A-F]{4}) AQ(\s)', line)
    if m:
        line = m.group(1) + ' A7' + m.group(2) + line[len(m.group(0)):]
        return line

    # Handle CABBOS -> CAB B05 -> two chars should be space+mnemonic
    # This is probably "CA BB 05" pattern -> skip for now

    # Pattern: address space hex-bytes space/tab mnemonic
    # Allow various OCR garbage in hex bytes
    m = re.match(r'^([0-9A-F]{4}) ([0-9A-Fa-f£€O&]{2,8})(\s)', line)
    if m:
        hex_part = m.group(2)
        fixed = hex_part.upper()  # Uppercase first
        fixed = fixed.replace('£', 'E')
        fixed = fixed.replace('€', 'C')
        fixed = fixed.replace('O', '0')  # Be careful - only in hex context
        # Remove & which is OCR garbage
        fixed = fixed.replace('&', '')

        if fixed != hex_part and len(fixed) >= 2 and len(fixed) <= 6:
            line = m.group(1) + ' ' + fixed + m.group(3) + line[len(m.group(0)):]
        return line

    # Pattern: address space hex-bytes at end of line (data bytes, no mnemonic)
    m = re.match(r'^([0-9A-F]{4}) ([0-9A-Fa-f£€O&]{2,8})$', line)
    if m:
        hex_part = m.group(2)
        fixed = hex_part.upper()
        fixed = fixed.replace('£', 'E')
        fixed = fixed.replace('€', 'C')
        fixed = fixed.replace('O', '0')
        fixed = fixed.replace('&', '')

        if fixed != hex_part and len(fixed) >= 2 and len(fixed) <= 6:
            line = m.group(1) + ' ' + fixed
        return line

    return line


def fix_pipe_lines(line: str) -> str:
    """Remove standalone pipe characters (page breaks)."""
    if line.strip() == '|':
        return None
    return line


def fix_known_address_errors(line: str) -> str:
    """Fix specific known address OCR errors."""
    # Pattern: address starts line, followed by space and hex

    # Fix addresses with ? (should be F or other hex)
    line = re.sub(r'^([0-9A-F]{3})\?(\s)', r'\g<1>F\2', line)

    # Fix addresses with £ (should be E)
    line = re.sub(r'^([0-9A-F]*)\£([0-9A-F]*\s)', r'\g<1>E\2', line)

    # Fix addresses that are too long due to duplicated chars like 03Cc1 -> 03C1
    m = re.match(r'^([0-9A-F]{2})([A-F])([a-f])([0-9])\s', line)
    if m:
        # Pattern: 03Cc1 -> 03C1
        line = m.group(1) + m.group(2) + m.group(4) + line[5:]

    # Fix addresses with lowercase letters that should be uppercase
    m = re.match(r'^([0-9A-Fa-f]{4})\s', line)
    if m:
        addr = m.group(1)
        fixed_addr = addr.upper()
        if fixed_addr != addr:
            line = fixed_addr + line[4:]

    # Fix address like 0303 that should be 03D3 (based on context - hard to do automatically)

    return line


def fix_operand_garbage(line: str) -> str:
    """Fix garbage in operands."""
    # Fix «4H -> H, «H -> H for PUSH/POP
    if 'PUSH' in line or 'POP' in line:
        line = re.sub(r'\t«[0-9]*([A-Z])', r'\t\1', line)
        line = re.sub(r'\t([A-Z])\s+«', r'\t\1\t;', line)  # trailing garbage becomes comment
        # Fix PUSH =H -> PUSH H, PUSH -B -> PUSH B, etc.
        line = re.sub(r'(PUSH|POP)\t[-=]([A-Z])', r'\1\t\2', line)
        line = re.sub(r'(PUSH|POP)\t[-=]$', r'\1\tPSW', line)  # PUSH - probably PUSH PSW

    # Fix ) -> D for POP D
    if 'POP' in line and '\t)' in line:
        line = line.replace('\t)', '\tD')

    # Fix period -> comma in register operands (MOV A.M -> MOV A,M)
    line = re.sub(r'(MOV\t[A-Za-z])\.([A-Za-z])', r'\1,\2', line)
    line = re.sub(r'(LXI\t[A-Za-z])\.', r'\1,', line)
    line = re.sub(r'(MVI\t[A-Za-z])\.', r'\1,', line)

    # Fix missing comma in MOV (MOV BM -> MOV B,M)
    line = re.sub(r'MOV\t([A-Za-z])([A-Za-z])(\s|$)', r'MOV\t\1,\2\3', line)

    # Fix L misread as comma (MOV DLA -> MOV D,A, MOV BLM -> MOV B,M)
    line = re.sub(r'MOV\t([A-Za-z])L([A-Za-z])(\s|$)', r'MOV\t\1,\2\3', line)

    # Fix O as register (should be A)
    line = re.sub(r'MOV\t([A-Za-z]),O(\s|$)', r'MOV\t\1,A\2', line)
    line = re.sub(r'MOV\tO,([A-Za-z])', r'MOV\tA,\1', line)

    # Fix missing comma in LXI (LXI H0000 -> LXI H,0000)
    line = re.sub(r'LXI\t([A-Za-z])([0-9A-Fa-f])', r'LXI\t\1,\2', line)

    # Fix MVI with O as register (should be A, since O looks like 0 but is letter)
    line = re.sub(r'MVI\tO,', r'MVI\tA,', line)
    line = re.sub(r'MVI\t0,', r'MVI\tA,', line)  # Also 0 as register

    # Fix missing comma in MVI (MVI A00 -> MVI A,00)
    line = re.sub(r'MVI\t([A-Za-z])([0-9A-Fa-f])', r'MVI\t\1,\2', line)

    # Fix LXI H, ;VALUE -> LXI H,VALUE (semicolon mistakenly inserted)
    line = re.sub(r'(LXI\t[A-Za-z]),\s*;([A-Za-z0-9])', r'\1,\2', line)
    line = re.sub(r'(MVI\t[A-Za-z]),\s*;([A-Za-z0-9])', r'\1,\2', line)

    # Fix MVI E ;, VALUE -> MVI E,VALUE (semicolon and comma swapped)
    line = re.sub(r'(MVI\t[A-Za-z])\s+;,\s*([A-Za-z0-9])', r'\1,\2', line)

    # Fix CC/Cc -> C (doubled register, case insensitive)
    line = re.sub(r'\t[Cc][Cc]\b', r'\tC', line)
    line = re.sub(r',[Cc][Cc]\b', r',C', line)

    # Fix CPI with single lowercase letter that should be quoted
    # CPI a where hex is FE22 means CPI '"' (ASCII 22H = double quote)
    line = re.sub(r'CPI\ta(\s|$)', r"CPI\t'\"'\1", line)
    line = re.sub(r'CPI\te(\s|$)', r"CPI\t'\"'\1", line)

    # Fix CPI "   ; (space char, misread) -> CPI ' '
    line = re.sub(r'CPI\t"\s+;', "CPI\t' '\t;", line)
    # Fix CPI "oe -> CPI ' ' (space char)
    line = re.sub(r'CPI\t"oe\b', "CPI\t' '", line)
    # Fix CPI "o" -> CPI '0' (zero char)
    line = re.sub(r'CPI\t"o"\b', "CPI\t'0'", line)
    # Fix CPI "a" -> CPI 'a' (lowercase a)
    line = re.sub(r'CPI\t"a"\b', "CPI\t'a'", line)
    # Fix CPI "A" -> CPI 'A' (uppercase A)
    line = re.sub(r'CPI\t"A"\b', "CPI\t'A'", line)
    # Fix CPI "p" -> CPI 'D' (D char, based on FE44)
    line = re.sub(r'CPI\t"p"\b', "CPI\t'D'", line)
    # Fix CPI "i" -> CPI 'I' (I char, based on FE49)
    line = re.sub(r'CPI\t"i"\b', "CPI\t'I'", line)
    # Fix CPI "RY -> CPI 'R' (R char, based on FE52)
    line = re.sub(r'CPI\t"RY\b', "CPI\t'R'", line)
    # Fix CPI "y" -> CPI ')' (close paren, based on FE29)
    line = re.sub(r'CPI\t"y"\b', "CPI\t')'", line)
    # Fix CPI "wn -> CPI ',' (comma, based on FE2C)
    line = re.sub(r'CPI\t"wn\b', "CPI\t','", line)
    # Fix CPI "3 -> CPI 0A0H (based on FEA0)
    line = re.sub(r'CPI\t"3\b', "CPI\t0A0H", line)
    # Fix CPI "yn -> CPI '\"' (double quote)
    line = re.sub(r'CPI\t"yn\b', "CPI\t'\"'", line)

    # Fix mnemonic OCR errors
    line = re.sub(r'\bJUMP\b', 'JMP', line)
    line = re.sub(r'\bMP\t', 'JMP\t', line)  # MP -> JMP (missing J)
    line = re.sub(r'\bDZ\t', 'JZ\t', line)   # DZ -> JZ (D misread as J)
    line = re.sub(r'\bTHID\t', 'LHLD\t', line)  # THID -> LHLD
    line = re.sub(r'\bNVI\t', 'MVI\t', line)   # NVI -> MVI
    line = re.sub(r'\bMVT\t', 'MVI\t', line)   # MVT -> MVI
    line = re.sub(r'\bLXT\t', 'LXI\t', line)   # LXT -> LXI
    line = re.sub(r'\bLOAX\t', 'LDAX\t', line) # LOAX -> LDAX
    line = re.sub(r'\bOCR\t', 'DCR\t', line)   # OCR -> DCR
    line = re.sub(r'\bOW\s', 'DW\t', line)     # OW -> DW (O misread as D)
    line = re.sub(r'^\tNZ\t', '\tJNZ\t', line) # NZ -> JNZ (missing J)
    line = re.sub(r'^\tNc\t', '\tJNC\t', line) # Nc -> JNC
    line = re.sub(r'^\tNC\t', '\tJNC\t', line) # NC -> JNC
    line = re.sub(r'^\tUZ\t', '\tJZ\t', line)  # UZ -> JZ (U misread as J)
    line = re.sub(r'^\tXI\t', '\tLXI\t', line) # XI -> LXI (missing L)
    line = re.sub(r'^\tuP\s', '\tJP\t', line)  # uP -> JP
    line = re.sub(r'\sUZ\t', '\tJZ\t', line)   # UZ -> JZ (in listing lines)
    line = re.sub(r'\sXI\t', '\tLXI\t', line)  # XI -> LXI
    line = re.sub(r'\suP\s', '\tJP\t', line)   # uP -> JP

    # More mnemonic fixes
    line = re.sub(r'\bONC\b', 'JNC', line)     # ONC -> JNC (O misread as J)
    line = re.sub(r'\bJINZ\t', 'JNZ\t', line)  # JINZ -> JNZ (extra I)
    line = re.sub(r'\bJDZ\t', 'JZ\t', line)    # JDZ -> JZ (extra D)
    line = re.sub(r'\bOP\t', 'JP\t', line)     # OP -> JP (O misread as J)
    line = re.sub(r'\bLST\t', 'RST\t', line)   # LST -> RST (L misread as R)
    line = re.sub(r'\bORT\t', 'ORI\t', line)   # ORT -> ORI
    line = re.sub(r'\bET\t', 'RET\t', line)    # ET -> RET (missing R)
    line = re.sub(r'\bcc\t', 'JZ\t', line)     # cc -> JZ (OCR error)
    line = re.sub(r'\bLXE\t', 'LXI\t', line)   # LXE -> LXI (E misread as I)
    line = re.sub(r'\bEt\t', 'RET\t', line)    # Et -> RET (missing R)
    line = re.sub(r'\bB1\t', 'ORA\t', line)    # B1 (opcode) is ORA C, might be misread line
    line = re.sub(r'\bDO\t', 'DB\t', line)     # DO -> DB
    line = re.sub(r'\bADO\t', 'ADD\t', line)   # ADO -> ADD
    line = re.sub(r'\bUMP\t', 'JMP\t', line)   # UMP -> JMP (missing J)
    line = re.sub(r'\bLHLO\t', 'LHLD\t', line) # LHLO -> LHLD (O->D)
    line = re.sub(r'\bOMP\t', 'JMP\t', line)   # OMP -> JMP (O->J)
    line = re.sub(r'\bONZ\t', 'JNZ\t', line)   # ONZ -> JNZ (O->J)
    line = re.sub(r'\bJNE\t', 'JNZ\t', line)   # JNE -> JNZ (not valid 8080)
    line = re.sub(r'\bAZ\t', 'JZ\t', line)     # AZ -> JZ (missing J)
    line = re.sub(r'^\tNZ\t', '\tJNZ\t', line) # NZ -> JNZ (missing J)

    # Fix MOV A.M -> MOV A,M (period -> comma)
    line = re.sub(r'MOV\s+([A-Z])\.([A-Z])', r'MOV\t\1,\2', line)

    # Fix CALL/JMP with - as operand where label is in comment
    # Pattern: CALL - ;LABELNAME -> CALL LABELNAME
    line = re.sub(r'(CALL|JMP|JZ|JNZ|JC|JNC|JP|JM|JPE|JPO)\t--?\s*;([A-Za-z][A-Za-z0-9]*)', r'\1\t\2', line)

    # Fix trailing = after label operand (garbage before comment)
    line = re.sub(r'(JZ|JNZ|JC|JNC|JP|JM|CALL|JMP)\t([A-Za-z][A-Za-z0-9]*)\s+=\s*(;|$)', r'\1\t\2\t\3', line)

    # Fix SUB ) -> SUB D (D misread as ))
    line = re.sub(r'\bSUB\t\)', r'SUB\tD', line)

    # Fix trailing | after operand (page marker)
    line = re.sub(r'\+128\s+\|', '+128', line)
    line = re.sub(r'\s+\|$', '', line)

    # Fix my" -> ':' (common OCR error for ':')
    line = re.sub(r"\bmy\"", "':'", line)

    # Fix POPHL3RT -> POPHLRET (3 misread as E)
    line = re.sub(r'\bPOPHL3RT\b', 'POPHLRET', line)

    # Fix s= -> ; (comment marker OCR)
    line = re.sub(r'\ss=', '\t;', line)
    line = re.sub(r'\ss([A-Z])', r'\t;\1', line)

    # Fix s before lowercase word to be ; (comment)
    # Pattern: operand followed by spaces then sLowercase -> ; comment
    line = re.sub(r'(\t\S+\s+)s([a-z][a-z])', r'\1;\2', line)

    # Fix DB lines with trailing garbage after 0 (message terminator)
    # ",0      s; -> ",0 ;
    line = re.sub(r'",0\s+s;', '",0\t;', line)

    # Fix 1. -> 1 in DB lines (trailing period garbage)
    line = re.sub(r'(DB\s+)1\.(\s+;)', r'\g<1>1\2', line)

    # Fix EQU with label operand followed by garbage : (should be ; for comment)
    line = re.sub(r'(EQU\s+[A-Za-z][A-Za-z0-9]*)\s+:\s+', r'\1\t;', line)

    # Fix trailing : after label operands in LDA/STA
    line = re.sub(r'(LDA|STA|LHLD|SHLD)\s+([A-Za-z][A-Za-z0-9]*)\s+:\s*$', r'\1\t\2', line)

    # Fix 'z+ -> 'z' (missing close quote, + is garbage)
    line = re.sub(r"'([a-z])\+\s", r"'\1'\t", line)

    # Fix 'Z+1 -> 'Z'+1 (missing close quote)
    line = re.sub(r"'([A-Z])\+1\b", r"'\1'+1", line)

    # Fix "A-'a - -> 'A'-'a' (quote errors)
    line = re.sub(r'"A-\'a -', "'A'-'a'\t", line)

    # Fix 'a-'A = -> 'a'-'A' (missing close quote and trailing =)
    line = re.sub(r"'a-'A\s+=", "'a'-'A'\t", line)

    # Fix CMP B followed by text (missing semicolon)
    line = re.sub(r'(CMP\s+[A-Z])\s{2,}([A-Z])', r'\1\t;\2', line)

    # Fix label followed by many spaces and : (should be ; for comment)
    line = re.sub(r'(\t[A-Za-z][A-Za-z0-9]*)\s{5,}:\s*$', r'\1', line)

    # Fix MVI E, ; -> MVI D, where hex opcode is 16 (comment contains operand)
    # Pattern: MVI E,  ;OPERAND -> MVI D,OPERAND
    line = re.sub(r'MVI\tE,\s+;([A-Za-z0-9\-+]+)', r'MVI\tD,\1', line)

    # Fix CALL label followed by text (missing semicolon before comment)
    line = re.sub(r'(CALL\s+[A-Za-z][A-Za-z0-9]*)\s{2,}([A-Z][A-Z])', r'\1\t;\2', line)

    # Fix JNZ label followed by text (missing semicolon)
    line = re.sub(r'(JNZ\s+[A-Za-z][A-Za-z0-9]*)\s{2,}([A-Z])', r'\1\t;\2', line)

    # Fix DAD - -> DAD B (- misread as B or D)
    line = re.sub(r'DAD\t-\s', 'DAD\tB\t', line)

    # Fix PUSH - -> PUSH PSW (- is misread PSW)
    line = re.sub(r'PUSH\t-\s', 'PUSH\tPSW\t', line)
    # Fix PUSH -- -> PUSH PSW (-- is misread PSW)
    line = re.sub(r'PUSH\t--\s', 'PUSH\tPSW\t', line)
    # Fix PUSH i) -> PUSH D (i) misread)
    line = re.sub(r'PUSH\ti\)', 'PUSH\tD', line)
    # Fix PUSH 0 -> PUSH D (0 misread as D)
    line = re.sub(r'PUSH\t0\b', 'PUSH\tD', line)

    # Fix PUSH B : -> PUSH B (trailing garbage)
    line = re.sub(r'(PUSH\s+[A-Z])\s+:\s*(;|$)', r'\1\t\2', line)

    # Fix MOV C,8 -> MOV C,B (8 misread as B)
    line = re.sub(r'MOV\t([A-Z]),8\b', r'MOV\t\1,B', line)

    # Fix Jz -> JZ (lowercase z)
    line = re.sub(r'\bJz\b', 'JZ', line)

    # Fix POP sod -> POP D (lowercase, misread)
    line = re.sub(r'POP\tsod', 'POP\tD', line)
    line = re.sub(r'POP\tSOD', 'POP\tD', line)

    return line


def process_line(line: str) -> str:
    """Process a single line with conservative fixes."""
    if not line.strip():
        return line

    # Remove pipe lines
    result = fix_pipe_lines(line)
    if result is None:
        return None
    line = result

    # Skip headers
    if line.startswith('===') or 'basIC.LST' in line:
        return line

    # Apply fixes - garbage chars first to convert em-dashes
    line = fix_garbage_chars(line)
    line = fix_address_ocr(line)
    line = fix_hex_bytes(line)
    line = fix_known_address_errors(line)
    line = fix_comment_marker(line)
    line = fix_ocr_values(line)
    line = fix_operand_garbage(line)

    return line


def process_file(input_path: str, output_path: str):
    """Process the file."""
    with open(input_path, 'r') as f:
        lines = f.readlines()

    output_lines = []
    fixes = 0
    removed = 0

    for line_num, line in enumerate(lines, 1):
        orig = line.rstrip()
        fixed = process_line(orig)

        if fixed is None:
            removed += 1
            continue

        if fixed != orig:
            fixes += 1

        output_lines.append(fixed)

    with open(output_path, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')

    print(f"Processed {len(lines)} lines")
    print(f"Made {fixes} fixes")
    print(f"Removed {removed} lines")
    print(f"Wrote {len(output_lines)} lines to {output_path}")


if __name__ == '__main__':
    input_file = 'AltairBASIC-1975-v1.txt'
    output_file = 'AltairBASIC-1975-v2.txt'

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    process_file(input_file, output_file)
