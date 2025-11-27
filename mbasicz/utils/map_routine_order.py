#!/usr/bin/env python3
"""
map_routine_order.py - Map routine order in a binary by finding patterns

This tool takes a list of routine patterns from one binary and finds their
order in another binary.

Usage:
    python3 map_routine_order.py <our_com> <ref_com> <our_sym> [--module MODULE]
"""

import sys
import argparse


def load_binary(path):
    with open(path, 'rb') as f:
        return f.read()


def load_symbols(path):
    syms = {}
    with open(path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    syms[parts[0]] = int(parts[1], 16)
                except ValueError:
                    pass
    return syms


def find_pattern(pattern, data, min_match=6):
    """Find best match for pattern in data."""
    pattern_len = len(pattern)
    best_pos = None
    best_score = 0

    for pos in range(len(data) - pattern_len):
        matches = sum(1 for i in range(pattern_len) if data[pos + i] == pattern[i])
        if matches > best_score:
            best_score = matches
            best_pos = pos

    if best_score >= min_match:
        return best_pos, best_score
    return None, best_score


# Module definitions - which symbols belong to which module
MODULE_SYMBOLS = {
    'bintrp': ['START', 'JMPINI', 'READY', 'MAIN', 'ERROR', 'NEWSTT', 'GONE', 'CHRGTR'],
    'bimisc': ['SCRATH', 'CLEAR', 'NEXT', 'SWAP', 'ERASE', 'RESTOR', 'STOP', 'CONT'],
    'biedit': ['ERREDT', 'EDIT', 'INLED', 'POPART', 'EDITRT'],
    'binlin': ['QINLIN', 'INLIN', 'SINLIN', 'SCNSEM'],
    'biptrg': ['DIM', 'PTRGET', 'PTRGT2', 'NOARYS', 'ERSFIN', 'BSERR'],
    'bistrs': ['STRO$', 'STR$', 'STRLIT', 'STROUT', 'GETSPA', 'CAT', 'LEN', 'ASC', 'CHR$',
               'LEFT$', 'RIGHT$', 'MID$', 'VAL', 'INSTR', 'FRE'],
    'bio': ['OUTDO', 'LPTOUT', 'TTYCHR', 'CONOUT', 'INCHR', 'CONIN', 'CRDO', 'ISCNTC', 'INKEY'],
    'biprtu': ['PRINUS'],
    'f4': ['FADDH', 'FADD', 'FSUB', 'NORMAL', 'ZERO', 'FONE', 'LOG', 'FMULT', 'FDIV',
           'SIGN', 'FLOAT', 'ABS', 'NEG', 'SGN', 'PUSHF', 'MOVFM', 'FCOMP', 'FRCINT',
           'INT', 'ISUB', 'IADD', 'DSUB', 'DADD', 'DMULT', 'DDIV', 'FIN', 'FOUT',
           'FOUTO', 'SQR', 'EXP', 'RND', 'COS', 'SIN', 'TAN', 'ATN'],
    'fiveo': ['WHILE', 'WEND', 'CALLS', 'CHAIN', 'COMMON', 'WRITE'],
    'dskcom': ['SAVE', 'LOAD', 'MERGE', 'CLOSE', 'FIELD', 'RSET', 'LSET'],
    'fivdsk': ['VARECS', 'PUT', 'GET', 'EOF', 'LOC', 'LOF'],
    'dcpm': ['NAME', 'OPEN', 'SYSTEM', 'RESET', 'KILL', 'FILES'],
    'init': ['INIT', 'INITSA', 'DSKDAT'],
}


def main():
    parser = argparse.ArgumentParser(description='Map routine order in reference binary')
    parser.add_argument('our_com', help='Our built .com file')
    parser.add_argument('ref_com', help='Reference .com file')
    parser.add_argument('our_sym', help='Our symbol table file')
    parser.add_argument('--module', help='Specific module to analyze')
    parser.add_argument('--pattern-len', type=int, default=10, help='Pattern length')
    args = parser.parse_args()

    ours = load_binary(args.our_com)
    ref = load_binary(args.ref_com)
    syms = load_symbols(args.our_sym)

    # Determine which symbols to search
    if args.module:
        search_syms = MODULE_SYMBOLS.get(args.module, [])
    else:
        search_syms = list(syms.keys())

    # Find each symbol in reference
    found = []
    for name in search_syms:
        if name not in syms:
            continue
        our_addr = syms[name]
        our_off = our_addr - 0x100
        if our_off < 0 or our_off + args.pattern_len > len(ours):
            continue

        pattern = ours[our_off:our_off + args.pattern_len]
        ref_pos, score = find_pattern(pattern, ref)

        if ref_pos is not None:
            ref_addr = ref_pos + 0x100
            found.append((ref_addr, name, our_addr, score))

    # Sort by reference address
    found.sort()

    print(f"Routine order in reference (module: {args.module or 'all'}):")
    print("-" * 60)
    for ref_addr, name, our_addr, score in found:
        diff = ref_addr - our_addr
        print(f"  0x{ref_addr:04X}: {name:12} (our: 0x{our_addr:04X}, diff={diff:+5d})")


if __name__ == '__main__':
    main()
