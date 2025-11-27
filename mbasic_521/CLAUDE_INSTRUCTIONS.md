# STRICT INSTRUCTIONS - DO NOT DEVIATE

## The Algorithm (ONLY do this):

1. Run: `safe_run.sh python3 utils/walk_compare.py`
2. It reports first opcode or immediate difference
3. Find that location in source code
4. Fix source to match reference
5. Rebuild: `safe_run.sh python3 src/um80 mbasic_src/FILE.mac -o out/FILE.rel`
6. Relink: `safe_run.sh python3 src/ul80 -o out/mbasic.com -s out/bintrp.rel out/f4.rel out/biptrg.rel out/biedit.rel out/biprtu.rel out/bio.rel out/bimisc.rel out/bistrs.rel out/binlin.rel out/fiveo.rel out/dskcom.rel out/dcpm.rel out/fivdsk.rel out/init.rel`
7. Check size: `safe_run.sh ls -la out/mbasic.com com/mbasic.com`
8. If sizes differ, GOTO step 1
9. If sizes match, compare bytes: `safe_run.sh cmp com/mbasic.com out/mbasic.com`

## Rules:
- NO theorizing about what might be different
- NO exploring other parts of code
- NO changing approach without user approval
- ONLY follow the algorithm above
- Use safe_run.sh for ALL commands
- Do NOT use Edit tool (causes screen garbling)

## Current state:
- walk_compare.py starts at 0x0CC9 and walks both binaries
- Reports first opcode or immediate operand difference
- Skips 16-bit address operands (they differ due to relocation)
