#!/usr/bin/env python3
"""Decode the keyword table from 8K BASIC"""

with open('8kbas.bin', 'rb') as f:
    f.seek(0x73)  # KEYWORDS start
    data = f.read(0x100)  # Read enough

keywords = []
current = []
for b in data:
    if b == 0x80:  # End of table marker
        break
    if b & 0x80:  # High bit set = first char of keyword
        if current:
            keywords.append(''.join(current))
        current = [chr(b & 0x7F)]
    else:
        current.append(chr(b))

if current:
    keywords.append(''.join(current))

print(f"Found {len(keywords)} keywords:")
for i, kw in enumerate(keywords):
    print(f"  {i}: {kw}")
