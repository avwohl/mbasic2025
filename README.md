# MBASIC 5.21 Source Reconstruction

For CP/M, the widely used and distributed version of Microsoft BASIC is 5.21. Unfortunately, the original source code for this version has been lost to time.

This project takes the nearest available 5.2x sources and reconstructs them to compile byte-for-byte identical to the original MBASIC 5.21 binary.

## Background

It has been a constant request on retro computing forums to get the MBASIC 5.21 sources. Some folks just want to learn how the interpreter works. Others want to add extensions for specific hardware or implement new features.

A set of sources labeled "MBASIC 5.2" exists, but while they are in the same family, they are clearly not the sources for 5.21. These original 5.2 sources are preserved in the `mbasic_52/` directory.

## Approach

1. A custom disassembler (ud80) was used to disassemble the original `mbasic.com` 5.21 binary
2. The disassembly was analyzed to identify differences from the 5.2 sources
3. Minimal changes were made to the 5.2 sources to generate a byte-for-byte match with 5.21
4. The reconstructed sources are in `mbasic_521/mbasic_src/`

## Project Structure

```
mbasic2025/
├── mbasic_52/          # Original MBASIC 5.2 sources (reference)
├── mbasic_521/         # recreated 5.21 sources
├── mbasicz/            # latest available, optimized for z80
├── 4k8k/               # 4k basic and 8k basic
│   ├── mbasic_src/     # Reconstructed 5.21 sources
│   ├── com/            # Reference mbasic.com 5.21 binary
│   ├── disasm/         # Disassembly of mbasic.com
│   ├── build.sh        # Build script
│   └── utils/          # Utility scripts
└── README.md
```

## Building

### Prerequisites

You need **um80**, a MACRO-80 compatible assembler toolchain for Linux.

Install from PyPI:
```bash
pip install um80
```

Or install from source:
```bash
git clone https://github.com/avwohl/um80_and_friends.git
cd um80_and_friends
pip install -e .
```

### Build Process

```bash
cd mbasic_521
./build.sh
```

This will:
1. Assemble all source modules (`.mac` files) into relocatable object files (`.rel`)
2. Link them together to produce `out/mbasic_go.com`
3. Generate a symbol file `out/mbasic_go.sym`

### um80 Toolchain

The um80 toolchain includes:

**um80** - MACRO-80 compatible assembler
```
um80 source.mac -o output.rel [-l listing.prn]
```

**ul80** - LINK-80 compatible linker
```
ul80 -o output.com [-s] file1.rel file2.rel ...
```
- `-s` generates a `.sym` symbol file
- `-x` outputs Intel HEX format
- `-p ORIGIN` sets program origin (default: 0x100)

## Source Modules

The interpreter is built from these modules (in link order):

| Module | Description |
|--------|-------------|
| bintrp.mac | Main interpreter core |
| f4.mac | Floating point math |
| biptrg.mac | Program storage/management |
| biedit.mac | Line editor |
| biprtu.mac | Print utilities |
| bio.mac | I/O routines |
| bimisc.mac | Miscellaneous functions |
| bistrs.mac | String handling |
| binlin.mac | Line input |
| fiveo.mac | File I/O |
| dskcom.mac | Disk commands |
| dcpm.mac | CP/M interface |
| fivdsk.mac | Disk file handling |
| init.mac | Initialization |

## License

The original MBASIC sources are copyright Microsoft. This reconstruction is provided for educational and historical preservation purposes.

## Links

- Project repository: https://github.com/avwohl/mbasic2025
- um80 assembler: https://github.com/avwohl/um80_and_friends
