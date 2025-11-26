#!/usr/bin/env python3
"""
ucref80 - Cross-reference utility for MACRO-80 assembly files.

Generates a cross-reference listing showing where symbols are defined
and referenced in assembly source files.

Usage: ucref80 [-o output.txt] file1.mac [file2.mac ...]
"""

import sys
import os
import argparse
import re
from collections import defaultdict


class Symbol:
    """Symbol cross-reference entry."""
    def __init__(self, name):
        self.name = name
        self.definitions = []  # List of (filename, line_num)
        self.references = []   # List of (filename, line_num)
        self.is_external = False
        self.is_public = False


class CrossReference:
    """Cross-reference generator."""

    def __init__(self):
        self.symbols = {}  # name -> Symbol
        self.current_file = ""
        self.files_processed = []

        # Patterns for parsing
        self.label_pattern = re.compile(r'^([A-Za-z_$@?][A-Za-z0-9_$@?]*)\s*:', re.IGNORECASE)
        self.equ_pattern = re.compile(r'^([A-Za-z_$@?][A-Za-z0-9_$@?]*)\s+(equ|set|defl)\s+', re.IGNORECASE)
        self.public_pattern = re.compile(r'^\s*public\s+(.+)', re.IGNORECASE)
        self.extrn_pattern = re.compile(r'^\s*extrn\s+(.+)', re.IGNORECASE)
        self.macro_pattern = re.compile(r'^([A-Za-z_$@?][A-Za-z0-9_$@?]*)\s+macro\b', re.IGNORECASE)

        # Reserved words that shouldn't be treated as symbols
        self.reserved = {
            # Directives
            'ORG', 'EQU', 'SET', 'DEFL', 'DB', 'DW', 'DS', 'DC', 'DEFB', 'DEFW', 'DEFS',
            'IF', 'ELSE', 'ENDIF', 'IFT', 'IFF', 'COND', 'ENDC',
            'IFDEF', 'IFNDEF', 'IFB', 'IFNB', 'IFIDN', 'IFDIF',
            'MACRO', 'ENDM', 'LOCAL', 'REPT', 'IRP', 'IRPC', 'EXITM',
            'PUBLIC', 'EXTRN', 'EXTERN', 'GLOBAL', 'ENTRY', 'EXT', 'NAME',
            'CSEG', 'DSEG', 'ASEG', 'COMMON',
            'END', 'TITLE', 'SUBTTL', 'PAGE', 'EJECT',
            '.Z80', '.8080', '.8085', '.PHASE', '.DEPHASE',
            '.LIST', '.XLIST', '.SALL', '.LALL', '.XALL', '.SFCOND', '.LFCOND',
            '.PRINTX', '.RADIX', '.REQUEST', '.COMMENT',
            'INCLUDE', 'INCBIN',
            # 8080/Z80 Instructions
            'MOV', 'MVI', 'LXI', 'LDA', 'STA', 'LHLD', 'SHLD', 'LDAX', 'STAX',
            'XCHG', 'PUSH', 'POP', 'XTHL', 'SPHL', 'PCHL',
            'ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP',
            'ADI', 'ACI', 'SUI', 'SBI', 'ANI', 'XRI', 'ORI', 'CPI',
            'INR', 'DCR', 'INX', 'DCX', 'DAD', 'DAA',
            'RLC', 'RRC', 'RAL', 'RAR', 'CMA', 'CMC', 'STC',
            'JMP', 'JC', 'JNC', 'JZ', 'JNZ', 'JP', 'JM', 'JPE', 'JPO',
            'CALL', 'CC', 'CNC', 'CZ', 'CNZ', 'CP', 'CM', 'CPE', 'CPO',
            'RET', 'RC', 'RNC', 'RZ', 'RNZ', 'RP', 'RM', 'RPE', 'RPO',
            'RST', 'EI', 'DI', 'NOP', 'HLT', 'RIM', 'SIM',
            'IN', 'OUT',
            # Z80 extensions
            'LD', 'EX', 'EXX', 'DJNZ', 'JR', 'JP', 'LDIR', 'LDDR', 'CPIR', 'CPDR',
            'NEG', 'CPL', 'SCF', 'CCF', 'HALT', 'RETI', 'RETN',
            'BIT', 'SET', 'RES', 'RL', 'RR', 'SLA', 'SRA', 'SRL', 'RLD', 'RRD',
            'IM', 'OTIR', 'OTDR', 'INIR', 'INDR', 'OUTI', 'OUTD', 'INI', 'IND',
            # Registers
            'A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'SP', 'PSW',
            'AF', 'BC', 'DE', 'HL', 'IX', 'IY', 'I', 'R',
            # Conditions
            'NZ', 'NC', 'PO', 'PE', 'P',
        }

    def get_symbol(self, name):
        """Get or create a symbol entry."""
        name = name.upper()
        if name not in self.symbols:
            self.symbols[name] = Symbol(name)
        return self.symbols[name]

    def add_definition(self, name, filename, line_num):
        """Record a symbol definition."""
        sym = self.get_symbol(name)
        sym.definitions.append((filename, line_num))

    def add_reference(self, name, filename, line_num):
        """Record a symbol reference."""
        sym = self.get_symbol(name)
        sym.references.append((filename, line_num))

    def is_reserved(self, name):
        """Check if a name is a reserved word."""
        return name.upper() in self.reserved

    def extract_symbols(self, text):
        """Extract potential symbol names from text."""
        # Remove strings
        text = re.sub(r"'[^']*'", "", text)
        text = re.sub(r'"[^"]*"', "", text)

        # Find all identifier-like tokens
        symbols = re.findall(r'[A-Za-z_$@?][A-Za-z0-9_$@?]*', text)
        return [s for s in symbols if not self.is_reserved(s)]

    def process_line(self, line, filename, line_num):
        """Process a single line of assembly source."""
        # Strip CR/LF and get original line
        line = line.rstrip('\r\n')

        # Remove comments
        if ';' in line:
            code_part = line.split(';')[0]
        else:
            code_part = line

        if not code_part.strip():
            return

        # Check for label definition (label at start of line with colon)
        match = self.label_pattern.match(code_part)
        if match:
            label = match.group(1)
            if not self.is_reserved(label):
                self.add_definition(label, filename, line_num)
            # Continue processing rest of line for references
            code_part = code_part[match.end():]

        # Check for EQU/SET/DEFL definition (symbol before EQU)
        match = self.equ_pattern.match(code_part)
        if match:
            symbol = match.group(1)
            if not self.is_reserved(symbol):
                self.add_definition(symbol, filename, line_num)
            # The expression after EQU may contain references
            code_part = code_part[match.end():]
            for sym in self.extract_symbols(code_part):
                self.add_reference(sym, filename, line_num)
            return

        # Check for MACRO definition
        match = self.macro_pattern.match(code_part)
        if match:
            macro_name = match.group(1)
            if not self.is_reserved(macro_name):
                self.add_definition(macro_name, filename, line_num)
            return

        # Check for PUBLIC declaration
        match = self.public_pattern.match(code_part)
        if match:
            symbols_text = match.group(1)
            for sym in self.extract_symbols(symbols_text):
                self.get_symbol(sym).is_public = True
            return

        # Check for EXTRN declaration
        match = self.extrn_pattern.match(code_part)
        if match:
            symbols_text = match.group(1)
            for sym in self.extract_symbols(symbols_text):
                s = self.get_symbol(sym)
                s.is_external = True
            return

        # Skip directives that contain text, not code
        upper_code = code_part.upper().strip()
        skip_directives = ['TITLE', 'SUBTTL', '.PRINTX', 'NAME', 'PAGE', 'EJECT',
                          '.COMMENT', '.SALL', '.LALL', '.XALL', '.LIST', '.XLIST',
                          '.SFCOND', '.LFCOND', '.RADIX', '.REQUEST']
        for directive in skip_directives:
            if upper_code.startswith(directive):
                return

        # For all other lines, extract symbol references
        # Skip the opcode/directive at the start
        parts = code_part.split(None, 1)
        if len(parts) > 1:
            operands = parts[1]
            for sym in self.extract_symbols(operands):
                self.add_reference(sym, filename, line_num)
        elif len(parts) == 1:
            # Could be a macro invocation
            potential_macro = parts[0]
            if not self.is_reserved(potential_macro):
                # Check if it's defined as a macro
                sym = self.symbols.get(potential_macro.upper())
                if sym and sym.definitions:
                    self.add_reference(potential_macro, filename, line_num)

    def process_file(self, filename):
        """Process an assembly source file."""
        self.current_file = os.path.basename(filename)
        self.files_processed.append(self.current_file)

        try:
            with open(filename, 'rb') as f:
                data = f.read()
        except IOError as e:
            print(f"Error reading {filename}: {e}", file=sys.stderr)
            return False

        # Handle CP/M format (strip ^Z and everything after)
        if b'\x1a' in data:
            data = data[:data.index(b'\x1a')]

        # Decode and split into lines
        try:
            text = data.decode('utf-8', errors='replace')
        except:
            text = data.decode('latin-1', errors='replace')

        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

        in_macro = False
        macro_depth = 0

        for line_num, line in enumerate(lines, 1):
            # Track macro depth (don't process macro bodies for references)
            upper_line = line.upper().strip()
            if re.match(r'^\w+\s+MACRO\b', upper_line) or upper_line.startswith('MACRO '):
                in_macro = True
                macro_depth += 1
            elif upper_line.strip() == 'ENDM':
                macro_depth -= 1
                if macro_depth <= 0:
                    in_macro = False
                    macro_depth = 0
                continue

            # Still process definitions inside macros, but skip reference tracking
            if in_macro:
                # Only look for definitions
                match = self.label_pattern.match(line)
                if match:
                    label = match.group(1)
                    if not self.is_reserved(label):
                        self.add_definition(label, self.current_file, line_num)
                continue

            self.process_line(line, self.current_file, line_num)

        return True

    def generate_report(self, output_file=None):
        """Generate the cross-reference report."""
        lines = []

        # Header
        lines.append("=" * 78)
        lines.append("CROSS REFERENCE LISTING")
        lines.append("=" * 78)
        lines.append("")
        lines.append(f"Files: {', '.join(self.files_processed)}")
        lines.append(f"Symbols: {len(self.symbols)}")
        lines.append("")
        lines.append("-" * 78)
        lines.append("")

        # Sort symbols alphabetically
        sorted_symbols = sorted(self.symbols.values(), key=lambda s: s.name)

        for sym in sorted_symbols:
            # Skip symbols with no definitions and no references
            if not sym.definitions and not sym.references:
                continue

            # Symbol name with flags
            flags = []
            if sym.is_public:
                flags.append("PUBLIC")
            if sym.is_external:
                flags.append("EXTRN")

            flag_str = f" ({', '.join(flags)})" if flags else ""
            lines.append(f"{sym.name}{flag_str}")

            # Definitions
            if sym.definitions:
                def_strs = []
                for filename, line_num in sym.definitions:
                    def_strs.append(f"{filename}:{line_num}")
                lines.append(f"  Defined:    {', '.join(def_strs)}")
            elif sym.is_external:
                lines.append(f"  Defined:    (external)")
            else:
                lines.append(f"  Defined:    ** UNDEFINED **")

            # References
            if sym.references:
                # Group references by file
                refs_by_file = defaultdict(list)
                for filename, line_num in sym.references:
                    refs_by_file[filename].append(line_num)

                ref_parts = []
                for filename in sorted(refs_by_file.keys()):
                    line_nums = sorted(set(refs_by_file[filename]))
                    # Format line numbers, wrapping if needed
                    nums_str = ', '.join(str(n) for n in line_nums)
                    ref_parts.append(f"{filename}: {nums_str}")

                # Wrap long reference lists
                ref_str = '; '.join(ref_parts)
                if len(ref_str) > 60:
                    lines.append(f"  References:")
                    for part in ref_parts:
                        lines.append(f"    {part}")
                else:
                    lines.append(f"  References: {ref_str}")
            else:
                lines.append(f"  References: (none)")

            lines.append("")

        # Summary
        lines.append("-" * 78)
        lines.append("")

        # Count statistics
        defined = sum(1 for s in sorted_symbols if s.definitions)
        external = sum(1 for s in sorted_symbols if s.is_external)
        public = sum(1 for s in sorted_symbols if s.is_public)
        undefined = sum(1 for s in sorted_symbols
                       if not s.definitions and not s.is_external and s.references)

        lines.append("SUMMARY")
        lines.append(f"  Total symbols:     {len(sorted_symbols)}")
        lines.append(f"  Defined:           {defined}")
        lines.append(f"  External:          {external}")
        lines.append(f"  Public:            {public}")
        if undefined:
            lines.append(f"  Undefined:         {undefined}")
        lines.append("")

        # Undefined symbols listing
        undefined_syms = [s for s in sorted_symbols
                        if not s.definitions and not s.is_external and s.references]
        if undefined_syms:
            lines.append("UNDEFINED SYMBOLS:")
            for sym in undefined_syms:
                lines.append(f"  {sym.name}")
            lines.append("")

        report = '\n'.join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Cross-reference written to {output_file}")
        else:
            print(report)

        return report


def main():
    parser = argparse.ArgumentParser(
        description='Generate cross-reference listing for MACRO-80 assembly files')
    parser.add_argument('inputs', nargs='+', help='Input .MAC files')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    # Check input files exist
    for filename in args.inputs:
        if not os.path.exists(filename):
            print(f"Error: File not found: {filename}", file=sys.stderr)
            sys.exit(1)

    # Process files
    cref = CrossReference()

    for filename in args.inputs:
        print(f"Processing {filename}...", file=sys.stderr)
        if not cref.process_file(filename):
            sys.exit(1)

    # Generate report
    cref.generate_report(args.output)


if __name__ == '__main__':
    main()
