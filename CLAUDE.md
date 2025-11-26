# Notes for Claude

## Terminal Output

- NEVER output raw binary data to the terminal - it can put the terminal in graphics mode and make output unreadable
- When displaying binary data, always use hex encoding (e.g., `.hex()` in Python)
- Use `xxd` or similar tools that produce safe ASCII output

## Binary Comparison Procedure

When comparing reference mbasic.com to our build:
1. Compare byte by byte from the beginning of the file
2. Skip address bytes in instructions (CALL, JMP, JZ, JNZ, LDA, STA, LHLD, SHLD, LXI, etc.) and DW data - these are relocations
3. Find the FIRST actual opcode or immediate data difference
4. Fix it in the source
5. Rebuild and repeat
6. Do NOT look ahead to later differences
7. Do NOT calculate, report, or think about total byte differences or percentages
