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
## Related Projects

- [80un](https://github.com/avwohl/80un) - Unpacker for the CP/M archive and compression formats LBR, ARC, squeeze, crunch, and CrLZH.
- [cpmdroid](https://github.com/avwohl/cpmdroid) - Z80/CP/M emulator for Android phones and tablets. It emulates the RomWBW HBIOS interface and a VT100 terminal.
- [cpmemu](https://github.com/avwohl/cpmemu) - Z80/CP/M emulator for Linux and Windows, with Z80 and 8080 CPU cores. It translates the BDOS and BIOS calls of CP/M 2.2 programs to the host file system.
- [ioscpm](https://github.com/avwohl/ioscpm) - Z80/CP/M emulator for iOS and macOS. It emulates the RomWBW HBIOS interface and runs CP/M 2.2 and CP/M 3.
- [learn-ada-z80](https://github.com/avwohl/learn-ada-z80) - Collection of more than 90 Ada example programs for uada80, the Ada compiler for the Z80 processor and CP/M.
- [mbasic](https://github.com/avwohl/mbasic) - Python interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. Two compiler backends compile the programs to CP/M .COM files or to JavaScript.
- [mbasicc](https://github.com/avwohl/mbasicc) - C++17 interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. It runs on Linux and macOS.
- [mbasicc_web](https://github.com/avwohl/mbasicc_web) - Web browser interpreter for MBASIC 5.21, the Microsoft BASIC-80 for CP/M. Emscripten compiles the mbasicc interpreter to WebAssembly.
- [mpm2](https://github.com/avwohl/mpm2) - Z80 emulator for MP/M II, the multi-user CP/M operating system. Users connect over SSH, and SFTP clients transfer files.
- [romwbw_emu](https://github.com/avwohl/romwbw_emu) - Hardware-level Z80/CP/M emulator for Linux and macOS. It emulates the RomWBW HBIOS interface and switches banks in 512 KB of ROM and 512 KB of RAM.
- [scelbal](https://github.com/avwohl/scelbal) - Floating-point BASIC interpreter for the 8080 processor and CP/M. A translator converts the original 8008 source code to 8080 source code.
- [uada80](https://github.com/avwohl/uada80) - Ada compiler for the Z80 processor and CP/M 2.2. It compiles a subset of Ada 2012 to CP/M .COM files.
- [uc80](https://github.com/avwohl/uc80) - C compiler for the Z80 processor and CP/M. It optimizes for small code size.
- [ucow](https://github.com/avwohl/ucow) - Cowgol compiler for the Z80 processor and CP/M. It runs on Linux in Python.
- [um80_and_friends](https://github.com/avwohl/um80_and_friends) - Linux toolchain that is compatible with Microsoft MACRO-80. It has an assembler, a linker, a librarian, and a disassembler.
- [upeepz80](https://github.com/avwohl/upeepz80) - Peephole optimizer for Z80 compilers that write lowercase Z80 assembly language. It shortens jumps to jr, builds djnz loops, and removes dead stores.
- [uplm80](https://github.com/avwohl/uplm80) - PL/M-80 compiler for the Z80 processor and CP/M. It writes Intel 8080 and Zilog Z80 assembly language.
- [z80cpmw](https://github.com/avwohl/z80cpmw) - Z80/CP/M emulator for Windows. It emulates the RomWBW HBIOS interface and boots CP/M from disk images.

