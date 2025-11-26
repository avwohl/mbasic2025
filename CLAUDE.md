# Notes for Claude

## Terminal Output

- NEVER output raw binary data to the terminal - it can put the terminal in graphics mode and make output unreadable
- When displaying binary data, always use hex encoding (e.g., `.hex()` in Python)
- Use `xxd` or similar tools that produce safe ASCII output
