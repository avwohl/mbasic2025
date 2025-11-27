#!/usr/bin/env python3
"""
compare_binaries.py - Compare two binary files and show statistics

Usage:
    python3 compare_binaries.py <file1> <file2>
"""

import sys
import argparse


def load_binary(path):
    with open(path, 'rb') as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description='Compare two binary files')
    parser.add_argument('file1', help='First binary file')
    parser.add_argument('file2', help='Second binary file')
    parser.add_argument('--show-diffs', type=int, default=0, help='Show first N differences')
    args = parser.parse_args()

    data1 = load_binary(args.file1)
    data2 = load_binary(args.file2)

    print(f"File 1: {args.file1} - {len(data1)} bytes")
    print(f"File 2: {args.file2} - {len(data2)} bytes")

    if len(data1) != len(data2):
        print(f"Size difference: {len(data1) - len(data2)} bytes")

    # Count differences
    min_len = min(len(data1), len(data2))
    diffs = []
    for i in range(min_len):
        if data1[i] != data2[i]:
            diffs.append(i)

    diff_count = len(diffs)
    print(f"Differing bytes: {diff_count} ({100*diff_count/min_len:.1f}%)")

    if args.show_diffs and diffs:
        print(f"\nFirst {min(args.show_diffs, len(diffs))} differences:")
        for i, off in enumerate(diffs[:args.show_diffs]):
            addr = off + 0x100
            print(f"  0x{addr:04X}: {data1[off]:02x} vs {data2[off]:02x}")

    # Find first difference
    if diffs:
        first_diff = diffs[0]
        print(f"\nFirst difference at offset 0x{first_diff:04X} (addr 0x{first_diff+0x100:04X})")

    # Find longest matching run
    max_run = 0
    max_run_start = 0
    run_start = 0
    run_len = 0
    for i in range(min_len):
        if data1[i] == data2[i]:
            if run_len == 0:
                run_start = i
            run_len += 1
        else:
            if run_len > max_run:
                max_run = run_len
                max_run_start = run_start
            run_len = 0
    if run_len > max_run:
        max_run = run_len
        max_run_start = run_start

    print(f"Longest identical run: {max_run} bytes at 0x{max_run_start+0x100:04X}")


if __name__ == '__main__':
    main()
