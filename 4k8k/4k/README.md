# 4K BASIC 4.0 - Reconstructed Source

This is a reconstruction of the lost source code for Altair 4K BASIC version 4.0, originally written by Bill Gates, Paul Allen, and Monte Davidoff for MITS (Micro Instrumentation and Telemetry Systems) in 1976.

## About This Reconstruction

The original source code for 4K BASIC has been lost to history. This project reconstructs annotated assembly source from the binary, producing source that assembles byte-for-byte identical to the original.

### Sources for Comments and Labels

The annotations in this reconstruction come from three sources:

1. **altairbasic.org** - Disassembly and annotations from an earlier version (3.2) of Altair BASIC. Most labels and code structure remain consistent between versions.

2. **ud80 Disassembler** - Raw disassembly output providing the instruction-level foundation.

3. **Claude.ai Analysis** - Additional analysis, label naming, and comprehensive comments explaining the code's function and purpose.

## Files

- `4kbas40.mac` - Fully annotated source with meaningful labels and comments
- `4kbas40_new.mac` - Raw disassembly that builds byte-exact to original
- `4kbas40.bin` - Original 4K BASIC 4.0 binary (3833 bytes)
- `build_4k.sh` - Build script

## Building

Requirements:
- Python 3
- um80 assembler/linker (`pip install um80`)

To build:

```bash
./build_4k.sh
```

The build script will:
1. Assemble the source using um80
2. Link to produce the binary
3. Verify the output matches the original byte-for-byte

A successful build displays:
```
SUCCESS: Output matches original binary!
```

## Reference Materials

The `ref/` directory contains materials from version 3.2:
- `4kbas32.rom` - Earlier 3.2 version binary
- `basic32_disasm.lst` - Disassembly listing
- `basic32_labels.txt` - Label definitions
- `label_map_32_to_40.txt` - Address mapping between versions

## Repository

This project is available on GitHub:

https://github.com/avwohl/mbasic2025

## Related Projects

- **um80** - 8080/Z80 macro assembler and linker used to build these sources
  - https://github.com/avwohl/um80_and_friends
  - `pip install um80`

## See Also

- [altairbasic.org](http://altairbasic.org/) - Source for 3.2 annotations
- Altair 8800 BASIC Reference Manual (July 1977)
- `../8k/` - Reconstructed 8K BASIC 4.0 source
- `../../mbasic_521/` - Reconstructed MBASIC 5.21 source
