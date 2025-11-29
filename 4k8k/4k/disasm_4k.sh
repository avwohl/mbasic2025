#!/bin/bash
# Disassemble 4K BASIC 4.0 with labels derived from BASIC 3.2 disassembly
# Reference: http://altairbasic.org/ and github.com/option8/Altair-BASIC
#
# Source file: 4kbas40.bin (3833 bytes = 0x0000-0x0EF8)
#
# BASIC 3.2 vs 4.0 differences:
# - Keywords at 0x51 (vs 0x57 in 3.2)
# - Error codes at 0x100 (vs 0xFA in 3.2)
# - Init at 0xDE6 (vs 0xD21 in 3.2)
# - Messages slightly relocated
#
# Memory Map:
# 0000-0003: Entry (DI, JMP Init)
# 0004-0007: System pointers
# 0008-0042: RST routines (SyntaxCheck, NextChar, OutChar, CompareHLDE, FTestSign, PushNextWord)
# 0043-0050: Function dispatch table (SGN, INT, ABS, USR, SQR, RND, SIN handlers)
# 0051-00CB: BASIC keywords (high-bit terminated strings)
# 00CC-00F3: Statement handler dispatch table
# 00F4-00FF: Arithmetic operator dispatch
# 0100-0117: Two-letter error codes (NF, SN, RG, OD, FC, OV, OM, UL, BS, DD, /0, ID)
# 0118-011E: System pointers
# 011F-0126: Zero-filled area
# 0127-0153: Startup messages (" BYTES FREE", "4K BASIC 4.0", "COPYRIGHT MITS 1976")
# 0154-0168: System pointers
# 0169-0188: System variables (FACCUM, etc.)
# 0189-0199: Messages (" ERROR", " IN ", "OK")
# 019A-0EBE: Main interpreter code
# 0EBF-0ED2: Optional function table (SIN/RND/SQR dispatch)
# 0ED3-0EF8: Prompt strings ("SIN", "RND", "SQR", "TERMINAL WIDTH", "MEMORY SIZE")

python3 -m um80.ud80 4kbas40.bin --org 0 -o 4kbas40_new.mac \
    -d 0004-0007 \
    -d 0026-0027 \
    -t 0043-004E \
    -d 004F-0050 \
    -l 004F,SinEntry \
    -l 0050,KW_INLINE_FNS_END \
    -dc 0051-00CB \
    -t 00CC-00F3 \
    -d 00F4-00FF \
    -da 0100-0117 \
    -d 0118-011E \
    -d 011F-0126 \
    -da 0127-0153 \
    -d 0154-0168 \
    -d 0169-0188 \
    -da 0189-0199 \
    -d 0EBF-0ED2 \
    -da 0ED3-0EF8 \
    -l 0000,Start \
    -l 0008,SyntaxCheck \
    -l 0010,NextChar \
    -l 0018,OutChar \
    -l 0020,CompareHLDE \
    -l 0026,TERMINAL_Y \
    -l 0027,TERMINAL_X \
    -l 0028,FTestSign \
    -l 003B,PushNextWord \
    -l 0043,KW_INLINE_FNS \
    -l 0051,KEYWORDS \
    -l 00CC,KW_GENERAL_FNS \
    -l 0100,ERROR_CODES \
    -l 011F,LINE_BUFFER \
    -l 0127,szByteFree \
    -l 0133,szVersion \
    -l 0140,szCopyright \
    -l 0189,szError \
    -l 0190,szIn \
    -l 0195,szOK \
    -e 0000 \
    -e 0008 \
    -e 0020 \
    -e 0028 \
    -e 003B \
    -l 019A,GetFlowPtr \
    -e 019A \
    -l 01AF,CopyMemoryUp \
    -e 01AF \
    -l 01BE,CheckEnoughVarSpace \
    -e 01BE \
    -l 01D3,OutOfMemory \
    -e 01D3 \
    -d 01D5-01DA \
    -l 01D6,SyntaxError \
    -l 01D8,DivByZero \
    -l 01DB,Error \
    -e 01DB \
    -d 01FC-01FE \
    -l 01FD,Stop \
    -l 01FE,StopPop \
    -l 01FF,StopCont \
    -e 01FF \
    -l 0201,Main \
    -e 0201 \
    -l 0207,GetNonBlankLine \
    -e 0207 \
    -l 029D,New \
    -e 029D \
    -l 029E,Run \
    -e 029E \
    -l 02A9,Clear \
    -e 02A9 \
    -l 02AE,ResetAll \
    -e 02AE \
    -l 02BD,ResetStack \
    -e 02BD \
    -l 0326,Tokenize \
    -e 0326 \
    -l 0349,InputLine \
    -e 0349 \
    -l 039F,List \
    -e 039F \
    -l 03E3,For \
    -e 03E3 \
    -l 03F0,PushStepValue \
    -e 03F0 \
    -l 0402,ExecNext \
    -e 0402 \
    -l 0422,Exec \
    -e 0422 \
    -l 0477,Restore \
    -e 0477 \
    -l 04A6,FunctionCallError \
    -e 04A6 \
    -l 04AB,LineNumberFromStr \
    -e 04AB \
    -l 04CC,Gosub \
    -e 04CC \
    -l 04DD,Goto \
    -e 04DD \
    -l 04ED,Return \
    -e 04ED \
    -d 0503-0506 \
    -l 0503,FindNextStatement \
    -l 0505,Rem \
    -l 0507,FindStmtLoop \
    -e 0507 \
    -l 0510,Let \
    -e 0510 \
    -l 0515,AssignVar \
    -e 0515 \
    -l 0524,If \
    -e 0524 \
    -l 0563,GetCompareOp \
    -e 0563 \
    -l 0565,Print \
    -e 0565 \
    -l 05B0,PrintString \
    -e 05B0 \
    -l 05D5,Tab \
    -e 05D5 \
    -l 05DA,PrintSpaces \
    -e 05DA \
    -l 05F2,Input \
    -e 05F2 \
    -l 0604,Read \
    -e 0604 \
    -l 0657,Next \
    -e 0657 \
    -l 0698,EvalExpression \
    -e 0698 \
    -l 069A,ArithParse \
    -e 069A \
    -l 06F7,EvalVarTerm \
    -e 06F7 \
    -l 0724,Dim \
    -e 0724 \
    -l 073C,GetVar \
    -e 073C \
    -l 07A2,GetArrayVar \
    -e 07A2 \
    -l 07CD,AllocArray \
    -e 07CD \
    -l 07EF,InitElements \
    -e 07EF \
    -l 080F,FAddMem \
    -e 080F \
    -l 081A,FSub \
    -e 081A \
    -l 0820,FAdd \
    -e 0820 \
    -l 08B7,FNormalise \
    -e 08B7 \
    -l 093F,FMul \
    -e 093F \
    -l 09A9,FDiv \
    -e 09A9 \
    -l 09CC,FZero \
    -e 09CC \
    -l 09E8,FTestSign_tail \
    -e 09E8 \
    -l 09F2,Sgn \
    -e 09F2 \
    -l 0A06,Abs \
    -e 0A06 \
    -l 0A08,FNegate \
    -e 0A08 \
    -l 0A85,FCompare \
    -e 0A85 \
    -l 0AB0,Int \
    -e 0AB0 \
    -l 0AF6,FIn \
    -e 0AF6 \
    -l 0B05,FInLoop \
    -e 0B05 \
    -l 0B3D,PrintIN \
    -e 0B3D \
    -l 0B45,PrintInt \
    -e 0B45 \
    -l 0B88,FOut \
    -e 0B88 \
    -l 0C05,FOut_tail \
    -e 0C05 \
    -l 0C19,ONE_HALF \
    -l 0C2F,Sqr \
    -e 0C2F \
    -l 0C6D,Rnd \
    -e 0C6D \
    -l 0CA0,Sin \
    -e 0CA0 \
    -l 0D24,TAYLOR_SERIES \
    -l 0D3D,InitCheckMem \
    -e 0D3D \
    -l 0D54,FindMemTopLoop \
    -e 0D54 \
    -l 0D9F,GetTerminalWidth \
    -e 0D9F \
    -l 0DBE,DoOptionalFns \
    -e 0DBE \
    -l 0DE6,Init \
    -e 0DE6 \
    -l 0E1D,InitProgramBase \
    -e 0E1D \
    -l 0E84,InitComplete \
    -e 0E84 \
    -l 0EBF,OPT_FN_DESCS \
    -l 0ED3,szSIN \
    -l 0ED7,szRND \
    -l 0EDB,szSQR \
    -l 0EDF,szTerminalWidth \
    -l 0EEE,szMemorySize \
    "$@"

echo "Disassembly written to 4kbas40_new.mac"
echo "Labels based on BASIC 3.2 disassembly from altairbasic.org"
