#!/usr/bin/env python3
"""
find_symbols.py - Find symbol patterns from one binary in another

This tool searches for byte patterns from a built .com file in a reference binary
to determine where routines appear in the reference.

Usage:
    python3 find_symbols.py <our_com> <ref_com> <our_sym> [--min-match N]
"""

import sys
import argparse


def load_binary(path):
    """Load a binary file."""
    with open(path, 'rb') as f:
        return f.read()


def load_symbols(path):
    """Load symbol table (name -> address)."""
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


def find_pattern(pattern, data, min_match=8):
    """Find best match for pattern in data.

    Returns (position, score) or (None, 0) if no good match.
    """
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


def main():
    parser = argparse.ArgumentParser(description='Find symbol patterns in reference binary')
    parser.add_argument('our_com', help='Our built .com file')
    parser.add_argument('ref_com', help='Reference .com file')
    parser.add_argument('our_sym', help='Our symbol table file')
    parser.add_argument('--min-match', type=int, default=8, help='Minimum matching bytes (default: 8)')
    parser.add_argument('--pattern-len', type=int, default=12, help='Pattern length (default: 12)')
    parser.add_argument('--symbols', nargs='*', help='Specific symbols to search (default: all)')
    args = parser.parse_args()

    # Load files
    ours = load_binary(args.our_com)
    ref = load_binary(args.ref_com)
    syms = load_symbols(args.our_sym)

    print(f"Our binary: {len(ours)} bytes")
    print(f"Reference: {len(ref)} bytes")
    print(f"Symbols loaded: {len(syms)}")
    print()

    # Filter symbols if specified
    if args.symbols:
        syms = {k: v for k, v in syms.items() if k in args.symbols}

    # Find each symbol in reference
    results = []
    for name, our_addr in sorted(syms.items(), key=lambda x: x[1]):
        our_off = our_addr - 0x100
        if our_off < 0 or our_off + args.pattern_len > len(ours):
            continue

        pattern = ours[our_off:our_off + args.pattern_len]
        ref_pos, score = find_pattern(pattern, ref, args.min_match)

        if ref_pos is not None:
            ref_addr = ref_pos + 0x100
            diff = ref_addr - our_addr
            results.append((name, our_addr, ref_addr, diff, score, args.pattern_len))
            print(f"{name:12} our:0x{our_addr:04X} ref:0x{ref_addr:04X} diff:{diff:+6d} ({score}/{args.pattern_len})")
        else:
            print(f"{name:12} our:0x{our_addr:04X} ref:?      no match ({score}/{args.pattern_len})")

    return results


if __name__ == '__main__':
    main()
