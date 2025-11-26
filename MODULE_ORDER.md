# MBASIC Module Link Order Analysis

## Executive Summary

Building 5.21 from the 5.22 sources requires more than reordering - the reference
binary has:
1. **Different module link order** - modules appear in completely different sequence
2. **Different f4.mac internal structure** - routines within f4 are rearranged
3. **Possible module interleaving** - f4 code may be split across other modules

An exact byte-for-byte match would require significant source restructuring.

---

## MAJOR FINDING: Different Module Link Order

Pattern matching reveals the 5.21 reference has modules in a completely different
order than our build.

### Our Build Order (from symbol addresses)
```
0x0100: bintrp
0x25C3: bimisc (SCRATH)
0x28ED: biedit (ERREDT)
0x2B0F: binlin (QINLIN)
0x2C4A: biptrg (SCNSEM)
0x2FED: bistrs (STRO$)
0x3470: bio (OUTDO)
0x365D: biprtu (PRINUS)
0x383A: f4 (FADDH)
0x4C56: fiveo (WHILE)
0x5379: dskcom (SAVE)
0x556F: fivdsk (VARECS)
0x5AE3: dcpm (NAME)
0x5D5B: init (INIT)
```

### Reference (5.21) Order (from pattern matching)
```
0x0100: bintrp (+ possibly some f4 early?)
0x3986: biptrg (DIM)         <- much later than our 0x2C63!
0x3CD5: biedit (ERREDT)      <- after biptrg
0x4320: bimisc (SCRATH)      <- very late, at 0x4320!
0x4948: bistrs (LEFT$)
0x4B28: binlin (INLIN)       <- appears AFTER bistrs!
0x4C58: fiveo (WHILE)
0x539A: dskcom (SAVE)
0x5865: dcpm (NAME)
0x5ACD: fivdsk (VARECS)
0x5D8C: init (INIT)
```

### Key Differences
| Module  | Our Address | Ref Address | Difference |
|---------|-------------|-------------|------------|
| bimisc  | 0x25C3      | 0x4320      | +7517 bytes |
| biedit  | 0x28ED      | 0x3CD5      | +5096 bytes |
| biptrg  | 0x2C63      | 0x3986      | +3363 bytes |
| binlin  | 0x2B0F      | 0x4B28      | +8190 bytes |
| bistrs  | 0x32AC      | 0x4948      | +5788 bytes |

---

## FINDING: f4.mac Internal Reorganization

The source code (5.22) has f4.mac routines in a different order than the reference (5.21).

### 5.22 Source Order (our f4.mac)
```
FADDH -> LOG -> FMULT -> FDIV -> SIGN -> ... -> INT -> ... -> SQR -> EXP -> RND -> COS -> SIN -> TAN -> ATN -> FOUT
```

### 5.21 Reference Order (from pattern matching)
```
FADDH -> ... -> FOUTO -> SQR -> EXP -> ... -> INT -> ... -> COS -> SIN -> ... -> LOG -> FMULT -> FDIV -> SIGN -> ... -> FOUT
```

### f4 Routine Position Differences
| Routine | Our Build | Reference | Difference | Notes |
|---------|-----------|-----------|------------|-------|
| FADDH   | 0x383A    | 0x3832    | -8         | Close - f4 start |
| SQR     | 0x49B6    | 0x3C12    | -3492      | Moved MUCH EARLIER |
| COS     | 0x4B62    | 0x3FE0    | -2946      | Moved EARLIER |
| SIN     | 0x4B68    | 0x3FE6    | -2946      | Moved EARLIER |
| LOG     | 0x397E    | 0x42BF    | +2369      | Moved MUCH LATER |
| FMULT   | 0x39C4    | 0x4305    | +2369      | Moved LATER |
| FDIV    | 0x3A2A    | 0x436B    | +2369      | Moved LATER |
| SIGN    | 0x3B00    | 0x4441    | +2369      | Moved LATER |
| FOUT    | 0x441F    | 0x4818    | +1017      | Moved later |

---

## Work Completed

### f4.mac Reordering
The f4.mac file was reordered to attempt to match 5.21's internal structure.
Original saved as: `mbasic_src/f4.mac.orig`

New block order:
1. header (lines 1-162)
2. faddh section (basic float ops)
3. fone_data (data tables)
4. fouto section (moved from end)
5. sqr, exp, polyx sections (moved from end)
6. fixer, int, dint, umult, isub, dsub sections
7. rnd section (moved from end)
8. cos_sin, tan, atn sections (moved from end)
9. ddiv section (moved)
10. log, fmult, div10, fdiv sections (moved)
11. sign section (moved)
12. remaining sections (pushf_mov, fcomp, frcint, qint, dmult, findbl, fin, fout)
13. atncon_end

### Result
After f4.mac reordering and rebuild:
- Our build: 24320 bytes (same as reference)
- Differing bytes: 20621 (84.8%)
- The reordering helped move f4 routines but didn't account for the different module link order

---

## Tools Created

See `utils/` directory:
- `find_symbols.py` - Find symbol patterns from one binary in another
- `map_routine_order.py` - Map routine order in a binary
- `compare_binaries.py` - Compare two binary files
- `reference_symbol_map.txt` - Documented symbol mappings found

---

## Next Steps to Match 5.21

To achieve an exact match would require:

1. **Determine exact reference link order**
   - The reference appears to link modules in order:
     bintrp -> ??? -> biptrg -> biedit -> bimisc -> bistrs -> binlin -> fiveo -> dskcom -> dcpm -> fivdsk -> init
   - Need to determine what comes between bintrp and biptrg (possibly part of f4?)

2. **Split f4.mac if necessary**
   - If f4 is truly interleaved with other modules, it may need to be split into multiple files

3. **Identify any code differences**
   - Some routines may have different implementations between 5.21 and 5.22

4. **Alternative: Accept differences**
   - Build a working 5.22 binary instead of exact 5.21 match

---

## Binary Comparison Statistics

| Metric | Value |
|--------|-------|
| Our build size | 24320 bytes |
| Reference size | 24320 bytes |
| Differing bytes | 20621 (84.8%) |
| bintrp size diff | ~32 bytes larger in reference |
| INIT position | Our 0x5D5B, Ref 0x5D8C (+49) |

---

## Files Modified

- `mbasic_src/f4.mac` - Reordered to attempt 5.21 match
- `mbasic_src/f4.mac.orig` - Backup of original 5.22 structure
- `out/f4.rel` - Rebuilt from reordered source
- `out/mbasic.com` - Rebuilt binary
- `out/mbasic.sym` - Rebuilt symbol table
