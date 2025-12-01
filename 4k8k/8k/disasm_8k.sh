#!/bin/bash
# Disassemble 8K BASIC 4.0 (Altair BASIC Rev. 4.0 EIGHT-K VERSION)
#
# Source file: 8kbas.bin (8192 bytes = 0x0000-0x1FFF)
# Runs on bare metal (not CP/M), loads at address 0
#
# Disassembly refined with trace data from altair_emu
#
# Memory Map (preliminary):
# 0000-0003: Entry (DI, JMP Init at 1A0B)
# 0004-0007: System pointers
# 0008-002F: RST routines (SyntaxCheck, NextChar, OutChar, CompareHLDE, FTestSign)
# 0030-0037: Unused (all zeros)
# 0038     : RST 7 entry (just RET)
# 0039-003C: MVI C,02 / CR LF
# 003D-0042: "BREAK\0" message
# 0043-0072: Statement/function dispatch table (address pairs)
# 0073-0154: BASIC keywords (rdc format - high bit on FIRST char of each keyword)
#            Statements: END,FOR,NEXT,DATA,INPUT,DIM,READ,LET,GOTO,RUN,IF,RESTORE,
#                        GOSUB,RETURN,REM,STOP,OUT,ON,NULL,WAIT,DEF,POKE,PRINT,CONT,
#                        LIST,CLEAR,CLOAD,CSAVE,NEW,TAB(,TO,FN,SPC(,THEN,NOT,STEP
#            Operators:  +,-,*,/,^,AND,OR,>,=,<
#            Functions:  SGN,INT,ABS,USR,FRE,INP,POS,SQR,RND,LOG,EXP,COS,SIN,TAN,ATN,
#                        PEEK,LEN,STR$,VAL,ASC,CHR$,LEFT$,RIGHT$,MID$
#            Note: CLOAD/CSAVE are cassette tape load/save (see Internet Archive .tap files)
# 0155-01A9: More dispatch tables (function addresses)
# 01AA-01CF: Two-letter error codes (NF,SN,RG,OD,FC,OV,OM,UL,BS,DD,/0,ID,TM,OS,LS,ST,CN,UF,MO)
# 01D0-0264: System variables area (initialized to 0 at runtime)
# 0265-0275: Messages (" ERROR\0", " IN \0", "OK\r\n\0")
# 0276-xxxx: Main interpreter code
# 1A0B-1B1A: Init routine
# 1B1B-1B2F: "WANT SIN-COS-TAN-ATN\0"
# 1B30-1B58: "\r\n\nWRITTEN FOR ROYALTIES BY MICRO-SOFT\r\n\0" (hidden message!)
# 1B59-1B67: "TERMINAL WIDTH\0"
# 1B68-1B73: "MEMORY SIZE\0"
# 1B74-1B80: " BYTES FREE\r\n"
# 1B81-1B97: "ALTAIR BASIC REV. 4.0\r\n"
# 1B98-1BAA: "[EIGHT-K VERSION]\r\n"
# 1BAB-1BC6: "COPYRIGHT 1976 BY MITS INC."
# 1BC7-1FFF: More code (trig functions, etc.)
#
# Hardware I/O Ports:
# Port 00H: Console status (88-SIO/88-2SIO) - bit 0=RX ready, bits 3,6,7=TX ready
# Port 01H: Console data (88-SIO/88-2SIO) - serial I/O
# Port 06H: Cassette status (88-ACR) - bit 0=input ready, bit 7=output ready
# Port 07H: Cassette data (88-ACR) - tape I/O for CLOAD/CSAVE
# Port 13H: Unknown (timing/status related)

python3 -m um80.ud80 8kbas.bin --org 0 -o 8kbas.mac \
    -d 0004-0007 \
    -da 003D-0042 \
    -t 0043-0072 \
    -dc 0073-0154 \
    -t 0155-01A9 \
    -da 01AA-01CF \
    -d 01D0-0264 \
    -da 0265-0275 \
    -da 1B1B-1BC6 \
    -l 0000,Start \
    -l 0008,SyntaxCheck \
    -l 0010,NextChar \
    -l 0018,OutChar \
    -l 0020,CompareHLDE \
    -l 0028,FTestSign \
    -l 0038,Rst7 \
    -l 003D,szBreak \
    -l 0043,STMT_DISPATCH \
    -l 0073,KEYWORDS \
    -l 0155,FN_DISPATCH \
    -l 01AA,ERROR_CODES \
    -l 0265,szError \
    -l 026C,szIn \
    -l 0271,szOK \
    -l 0276,GetFlowPtr \
    -l 1A0B,Init \
    -l 1B1B,szWantSinCosTanAtn \
    -l 1B30,szMicrosoft \
    -l 1B59,szTerminalWidth \
    -l 1B68,szMemorySize \
    -l 1B74,szBytesFree \
    -l 1B81,szVersion \
    -l 1B98,szEightK \
    -l 1BAB,szCopyright \
    -e 0000 \
    -e 0008 \
    -e 0010 \
    -e 0018 \
    -e 0020 \
    -e 0028 \
    -e 0038 \
    -e 0276 \
    -e 1A0B \
    -e 028E -e 0297 -e 02A6 -e 02C6 -e 03B1 -e 0444 -e 0465 -e 046E \
    -e 0495 -e 04D4 -e 04F4 -e 05B7 -e 05C9 -e 05DE -e 0653 -e 0681 \
    -e 06AD -e 06C0 -e 0752 -e 0773 -e 079C -e 07A8 -e 07B9 -e 07D5 \
    -e 07FA -e 0811 -e 0863 -e 087F -e 089B -e 08E0 -e 08ED -e 095E \
    -e 0988 -e 0A3A -e 0A94 -e 0B46 -e 0B9C -e 0C3F -e 0DF9 -e 0E6F \
    -e 0EE3 -e 0F00 -e 1041 -e 1050 -e 1061 -e 1071 -e 10A1 -e 10AB \
    -e 10D2 -e 1105 -e 110B -e 1159 -e 1185 -e 1200 -e 121C -e 131D \
    -e 1452 -e 1469 -e 1474 -e 1491 -e 1565 -e 15AD -e 15BC -e 1604 \
    -e 161B -e 1647 -e 1674 -e 16D3 -e 193A -e 1953 -e 196A -e 19B5 \
    -e 19D4 -e 1A5D -e 1ADD \
    "$@"

echo "Disassembly written to 8kbas.mac"
