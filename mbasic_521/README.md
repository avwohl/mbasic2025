# MBASIC 5.21 - Reconstructed Source

This is a reconstruction of the source code for Microsoft BASIC-80 (MBASIC) version 5.21 for CP/M, producing source that assembles byte-for-byte identical to the widely released `mbasic.com`.

## About This Reconstruction

No official source code for MBASIC 5.21 has ever been released. This project reconstructs working source by combining multiple sources and careful binary analysis.

### Sources

1. **MBASIC 5.2 Sources** - Partial source code for version 5.2 found on the web provided the foundation, including comments, labels, and code structure.

2. **mbasic.com v5.21** - The widely distributed CP/M binary served as the reference for byte-exact verification.

3. **ud80 Disassembler** - Used to disassemble the reference binary for comparison.

4. **Claude.ai Analysis** - Diffed code and binaries to identify differences between 5.2 and 5.21, making targeted changes to produce an exact match. Comments marked with `;5.21` indicate code that differs from the 5.2 sources.

## Building

Requirements:
- Python 3
- um80 assembler/linker (`pip install um80`)

To build:

```bash
./build.sh
```

The build script assembles all modules and links them in the correct order:
```
bintrp -> f4 -> biptrg -> biedit -> biprtu -> bio -> bimisc -> bistrs -> binlin -> fiveo -> dskcom -> dcpm -> fivdsk -> init
```

Output: `out/mbasic_go.com`

## Files

### Source Modules (`mbasic_src/`)

| Module | Description |
|--------|-------------|
| `bintrp.mac` | Main interpreter, tokenizer, reserved words |
| `f4.mac` | Floating point math routines |
| `biptrg.mac` | Program control (GOTO, GOSUB, etc.) |
| `biedit.mac` | Line editor |
| `biprtu.mac` | Print utilities |
| `bio.mac` | I/O routines |
| `bimisc.mac` | Miscellaneous functions |
| `bistrs.mac` | String handling |
| `binlin.mac` | Line input |
| `fiveo.mac` | Extended I/O |
| `dskcom.mac` | Disk commands |
| `dcpm.mac` | CP/M interface |
| `fivdsk.mac` | Disk file I/O |
| `init.mac` | Initialization |

### Other Files

- `com/mbasic.com` - Reference 5.21 binary (24320 bytes)
- `disasm/mbasic.mac` - Disassembly of reference binary
- `utils/` - Comparison and analysis tools

## Key Differences from 5.2

Code sections that differ from the 5.2 sources are marked with `;5.21` comments. Notable changes include:

- SIN function sign handling
- Reserved word table ordering
- GO/GOTO/GOSUB parsing structure

See `MODULE_ORDER.md` for detailed session notes on the reconstruction process.

## Repository

This project is available on GitHub:

https://github.com/avwohl/mbasic2025

## Related Projects

- **um80** - 8080/Z80 macro assembler and linker used to build these sources
  - https://github.com/avwohl/um80_and_friends
  - `pip install um80`

## See Also

- `../4k8k/4k/` - Reconstructed 4K BASIC 4.0 source
- `../4k8k/8k/` - Reconstructed 8K BASIC 4.0 source
