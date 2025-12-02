# 8K BASIC 4.0 - Reconstructed Source

This is a reconstruction of the lost source code for Altair 8K BASIC version 4.0, originally written by Bill Gates, Paul Allen, and Monte Davidoff for MITS (Micro Instrumentation and Telemetry Systems) in 1976.

## About This Reconstruction

Unlike 4K BASIC (which had commented 3.2 sources available at altairbasic.org), no commented source code for 8K BASIC has ever been published. This reconstruction was built entirely from binary analysis and cross-referencing with related BASIC versions.

### Sources for Comments and Labels

The annotations in this reconstruction come from four sources:

1. **4K BASIC Pattern Matching** - Comments were transferred from matching code sequences in the annotated 4K BASIC reconstruction, since both share common ancestry.

2. **MBASIC 5.21 Pattern Matching** - Additional comments were matched from the reconstructed MBASIC 5.21 sources, which evolved from 8K BASIC.

3. **cpmemu Code Tracing** - The cpmemu Altair emulator's code tracing feature was used to identify code vs. data regions and mark code entry points during execution.

4. **Claude.ai Analysis** - Comprehensive analysis to fill gaps, name labels, and explain code function and purpose.

### Comment Coverage

Currently 68% of source lines (4229 of 6190) contain comments.

## Files

- `8kbas_src.mac` - Annotated source with labels and comments
- `8kbas.bin` - Original 8K BASIC 4.0 binary
- `build_8k.sh` - Build script
- `tools/` - Pattern matching and label application utilities

## Building

Requirements:
- Python 3
- um80 assembler/linker (`pip install um80`)

To build:

```bash
./build_8k.sh
```

The build script will:
1. Assemble the source using um80
2. Link to produce the binary
3. Verify the output matches the original byte-for-byte

A successful build displays:
```
SUCCESS: Output matches original binary!
```

## Repository

This project is available on GitHub:

https://github.com/avwohl/mbasic2025

## Related Projects

- **um80** - 8080/Z80 macro assembler and linker used to build these sources
  - https://github.com/avwohl/um80_and_friends
  - `pip install um80`

- **cpmemu** - CP/M and Altair emulator with code tracing capability
  - https://github.com/avwohl/cpmemu

## See Also

- `../4k/` - Reconstructed 4K BASIC 4.0 source
- `../../mbasic_521/` - Reconstructed MBASIC 5.21 source
- Altair 8800 BASIC Reference Manual (July 1977)
