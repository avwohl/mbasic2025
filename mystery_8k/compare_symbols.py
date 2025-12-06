#!/usr/bin/env python3
"""
Compare expected symbols from OCR'd listing with reference 8K BASIC symbols.
"""

import sys


def load_expected_symbols(path):
    """Load expected symbols from EQU format file."""
    symbols = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            # Format: NAME    EQU    XXXXH
            parts = line.split()
            if len(parts) >= 3 and parts[1].upper() == 'EQU':
                name = parts[0]
                value_str = parts[2]
                if value_str.upper().endswith('H'):
                    try:
                        value = int(value_str[:-1], 16)
                        symbols[name.upper()] = value
                    except ValueError:
                        pass
    return symbols


def load_sym_file(path):
    """Load symbols from ul80 .sym file format."""
    symbols = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: XXXX NAME
            parts = line.split()
            if len(parts) >= 2:
                try:
                    value = int(parts[0], 16)
                    name = parts[1]
                    symbols[name.upper()] = value
                except ValueError:
                    pass
    return symbols


def compare_symbols(expected, reference):
    """Compare expected symbols with reference."""
    expected_names = set(expected.keys())
    reference_names = set(reference.keys())

    common = expected_names & reference_names
    only_expected = expected_names - reference_names
    only_reference = reference_names - expected_names

    print(f"Expected symbols: {len(expected)}")
    print(f"Reference symbols: {len(reference)}")
    print(f"Common symbols: {len(common)}")
    print(f"Only in expected (mystery): {len(only_expected)}")
    print(f"Only in reference (8kbas): {len(only_reference)}")
    print()

    # Check matching addresses
    matching = 0
    different = []
    for name in sorted(common):
        exp_val = expected[name]
        ref_val = reference[name]
        if exp_val == ref_val:
            matching += 1
        else:
            different.append((name, exp_val, ref_val))

    print(f"Symbols with matching addresses: {matching}")
    print(f"Symbols with different addresses: {len(different)}")
    print()

    if different:
        print("=== Symbols with different addresses ===")
        print(f"{'Name':<20} {'Expected':>8} {'Reference':>8} {'Diff':>8}")
        print("-" * 50)
        for name, exp_val, ref_val in sorted(different, key=lambda x: x[1]):
            diff = ref_val - exp_val
            print(f"{name:<20} {exp_val:04X}     {ref_val:04X}     {diff:+5d}")
        print()

    if only_expected:
        print(f"=== Symbols only in expected (mystery) - first 30 ===")
        for name in sorted(only_expected)[:30]:
            print(f"  {name:<20} = {expected[name]:04X}H")
        if len(only_expected) > 30:
            print(f"  ... and {len(only_expected) - 30} more")
        print()

    if only_reference:
        print(f"=== Symbols only in reference (8kbas) - first 30 ===")
        for name in sorted(only_reference)[:30]:
            print(f"  {name:<20} = {reference[name]:04X}H")
        if len(only_reference) > 30:
            print(f"  ... and {len(only_reference) - 30} more")


if __name__ == '__main__':
    expected_file = 'expected_symbols.txt'
    reference_file = '/tmp/8kbas_test.sym'

    if len(sys.argv) > 1:
        expected_file = sys.argv[1]
    if len(sys.argv) > 2:
        reference_file = sys.argv[2]

    expected = load_expected_symbols(expected_file)
    reference = load_sym_file(reference_file)

    compare_symbols(expected, reference)
