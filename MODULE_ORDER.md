# MBASIC 5.21 Recreation from 5.22 Sources

## Correct Link Order (CONFIRMED)

```
bintrp -> f4 -> biptrg -> biedit -> biprtu -> bio -> bimisc -> bistrs -> binlin -> fiveo -> dskcom -> dcpm -> fivdsk -> init
```

Build command:
```bash
ul80 -o out/mbasic.com -s \
  out/bintrp.rel out/f4.rel out/biptrg.rel out/biedit.rel \
  out/biprtu.rel out/bio.rel out/bimisc.rel out/bistrs.rel \
  out/binlin.rel out/fiveo.rel out/dskcom.rel out/dcpm.rel \
  out/fivdsk.rel out/init.rel
```

---

## Code Changes Made (5.22 -> 5.21)

### 1. SIN Function Sign Handling (f4.mac) - DONE

5.21 has extra code after `rc` to handle negative inputs by pushing NEG address:

```asm
sin:    lda   fac
        cpi   167o
        rc
        ; 5.21 adds 16 bytes here:
        lda   faclo+2     ; load sign byte (fac-1)
        ora   a           ; check sign
        jp    sinpos      ; skip if positive
        ani   7fh         ; clear sign bit
        sta   faclo+2     ; store back
        lxi   d,neg       ; address of neg routine
        push  d           ; push for return
sinpos:
        lxi   b,176q*256+042q   ; continue normal
```

**Note:** Must use `faclo+2` instead of `fac-1` due to um80 bug with negative offsets on external symbols.

---

## Known Issues

### um80 Assembler Bug

The um80 assembler incorrectly handles negative offsets on external symbols:
- `fac-1` assembles to `fac+1` instead of `fac-1`
- **Workaround:** Use `faclo+2` which equals the correct address

This affects all `fac-1` references in the codebase.

---

## Current Build Status

| Metric | Value |
|--------|-------|
| Reference size | 24320 bytes |
| Current build (with SIN fix) | 24336 bytes |
| Difference | +16 bytes |
| SIN code | MATCHES (only address relocations differ) |

The 16 extra bytes come from other 5.22 code changes not yet identified.

---

## Remaining Work

1. **Find 16 bytes to remove** - 5.22 has ~16 bytes of code somewhere that 5.21 doesn't have
   - Between FIN and INPRT there's ~55 extra bytes in 5.22
   - But offset changes cancel out across the binary

2. **Fix um80 external offset bug** - Either fix the assembler or change all `fac-1` to `faclo+2`

---

## Tools

See `utils/` directory:
- `find_symbols.py` - Find symbol patterns from one binary in another
- `map_routine_order.py` - Map routine order in a binary
- `compare_binaries.py` - Compare two binary files
- `reference_symbol_map.txt` - Documented symbol mappings

---

## Files

- `mbasic_src/f4.mac` - Modified with SIN fix
- `mbasic_src/f4.mac.orig` - Original 5.22 source
- `com/mbasic.com` - Reference 5.21 binary (MD5: 5fc6b24ecb203287d96e9e642ee4fc3b)
- `out/mbasic_order6.com` - Current build with SIN fix (24336 bytes)

---

## Session Notes (2024-11-26)

### Screen Garbling Issue
- The Edit tool output causes terminal to switch to DEC line-drawing mode
- Solution: Use `safe_run.sh` wrapper for all Bash commands, avoid Edit tool
- Wrapper location: `/home/wohl/mbasic2025/safe_run.sh`

### KLOOP Change (bintrp.mac)
Changed KLOOP structure from 5.22 to 5.21 style:
- 5.22: checks quote, space, THEN end-of-line
- 5.21: checks end-of-line FIRST, with crdone inline
- Made crdone label point to inline code at kloop (removed duplicate)
- **Result: No size change** - structures are equivalent in bytes

### SIN Code Verification
Both reference and our build have identical SIN sign-handling structure:
```
Reference SIN at 0x387F:
3A 07 0C FE 77 D8 3A 06 0C B7 F2 95 38 E6 7F 32
06 0C 11 74 28 D5 01 22 7E ...

Our build SIN at 0x3887:
3A 07 0C FE 77 D8 3A 06 0C B7 F2 9D 38 E6 7F 32
06 0C 11 4E 28 D5 01 22 7E ...
```
Only address operands differ (relocation), opcodes match.

### Current Status
- Reference: 24320 bytes
- Our build (order8): 24336 bytes  
- Difference: **16 bytes still unexplained**
- SIN code structure matches - not the source of difference
- KLOOP restructure had no effect on size

### Next Steps
- Use walk_compare.py to find where code actually diverges
- The 16 bytes must be somewhere else in the codebase
- Run: `safe_run.sh python3 utils/walk_compare.py`

---

## Session Notes (continued)

### Progress on walk_compare
- Fixed KLOOP inline crdone
- Fixed stuffh inline (moved from separate label)
- Fixed LXI B,notgos -> LXI D,notgos
- Fixed push b -> push d

### Current Difference: "GO " string comparison
At 0x0F98-0x0FBE, 5.21 has:
- LXI D,string_ptr  ; point to "GO " string
- CALL compare_loop ; subroutine at 0FBE
- JNZ ...

5.21 subroutine at 0FBE:
```
loop: LDAX D      ; get string char
      ORA A       ; end of string?
      RZ          ; yes, match!
      MOV C,A     ; save char
      CALL makupl ; uppercase input
      CMP C       ; compare
      RNZ         ; no match
      INX H       ; next input
      INX D       ; next string
      JMP loop
```
String "GO " at 0FCC: 47 4F 20 00

5.22 has inline: CPI 'G'; RNZ; INX H; CALL makupl; CPI 'O'; RNZ; ...

**This is likely the source of the 16-byte difference** - 5.22 inline code vs 5.21 loop+string.

### Next Step
Add the string comparison subroutine and replace inline CPI code with CALL to it.

### GO/GOTO/GOSUB Structure (Complex)

5.21 at 0x0F97-0FD6 (63 bytes total):
```
PUSH H
LXI D,gostr      ; "GO "
CALL strcm       ; string compare loop at 0FBE
JNZ notgos
CALL gskpsp      ; skip spaces (inline subroutine)
LXI D,tostr      ; "TO"
CALL strcm
MVI A,$goto
JZ gputrs
LXI D,ubstr      ; "UB"  
CALL strcm
JNZ notgos
MVI A,$gosub
gputrs: POP B
JMP notfn2

strcm: (0FBE)     ; string compare subroutine
  LDAX D / ORA A / RZ / MOV C,A / CALL makupl / CMP C / RNZ / INX H / INX D / JMP strcm

strings: "GO " "TO" "UB" (null terminated)
```

5.22 has inline CPI code (~30+ bytes just for character checks)

**Attempt to restructure failed** - adding the subroutine+strings actually increased size.
The 5.21 savings likely come from this routine being shared elsewhere in codebase.

### Files
- out/mbasic_order10.com - 24336 bytes (closest working build)
- Changes in order10: KLOOP crdone inline, stuffh inline, LXI D/PUSH D for notgos

### State
- Git checkout reverted bintrp.mac - need to re-apply order10 changes
- 16-byte difference still unexplained

## Session Notes (2024-11-26 continued)

### Reserved Word Table Reordering

Fixed the order of entries within the alpha-dispatch reserved word tables to match 5.21:

1. **atab**: Moved AUTO before AND
2. **dtab**: Moved DELETE to first position
3. **etab**: Moved ELSE before END
4. **ltab**: Moved LPRINT, LLIST, LPOS before LET, LINE, LOAD, LSET
5. **otab**: Moved OPEN before OUT
6. **ptab**: Moved PRINT before PUT
7. **rtab**: Moved RETURN before READ
8. **ttab**: Moved THEN before TRON

### GO Code Restructured (5.21 style)

Replaced 5.22 inline CPI-based GO handling with 5.21 strcm subroutine style:

```asm
; 5.21 structure
    push h           ; save text pointer
    lxi d,gostr      ; "GO " string
    call gostrcm     ; compare
    jnz notgos
    call chrgtr      ; advance
    lxi d,tostr      ; "TO"
    call gostrcm
    mvi a,$goto
    jz gputrs
    lxi d,ubstr      ; "UB"
    call gostrcm
    jnz notgos
    mvi a,$gosub
gputrs: pop b
    jmp notfn2
gostrcm: <14-byte subroutine>
gostr: db 'GO ',0
tostr: db 'TO',0
ubstr: db 'UB',0
```

GO code size: 63 bytes (matches reference)

### Current Status

- Reference: 24320 bytes
- Our build (mbasic_go.com): 24335 bytes
- Difference: **15 bytes still unexplained**

Both SIN and GO code structures match the reference. The 15-byte difference is elsewhere in the codebase.

### Files Modified

- `mbasic_src/bintrp.mac` - Table reordering + GO restructure
- `out/mbasic_go.com` - Current best build

### Next Steps

Continue walk_compare from data section (past 0x0700) to find structural code differences.
