# Altair 8800 BASIC Reference Manual

**Version 4.0 - January 1977**

MITS Inc. - A subsidiary of Pertec Computer Corporation

---

## Preface

The Altair BASIC language is a high-level programming language specifically designed for interactive computing systems. Its simple English-like instructions are easily understood and quickly learned, and its interactive nature allows instant feedback of results and diagnostics. Despite its simplicity, Altair BASIC has evolved into a powerful language with provisions for editing and string processing as well as numerical computation.

The Altair BASIC interpreter reads the instructions of the BASIC language and directs the Altair 8800 series microcomputer to execute them. Altair BASIC includes many useful diagnostic and editing features in all versions. The Extended versions provide additional features including comprehensive file input/output procedures in the disk version.

This manual explains the features of the BASIC language and the special provisions of the 4K, 8K, Extended and Disk Extended Altair BASIC interpreters.

---

## Table of Contents

1. [Some Introductory Remarks](#1-some-introductory-remarks)
2. [Expressions and Statements](#2-expressions-and-statements)
3. [Functions](#3-functions)
4. [Strings](#4-strings)
5. [Extended Features](#5-extended-features)
6. [Quick Reference](#6-quick-reference)

**Appendices:**
- [A: ASCII Character Codes](#appendix-a-ascii-character-codes)
- [B: Loading BASIC](#appendix-b-loading-basic)
- [C: Space and Speed Hints](#appendix-c-space-and-speed-hints)
- [D: Mathematical Functions](#appendix-d-mathematical-functions)
- [E: BASIC and Assembly Language](#appendix-e-basic-and-assembly-language)
- [F: Using the ACR Interface](#appendix-f-using-the-acr-interface)
- [G: Converting BASIC Programs](#appendix-g-converting-basic-programs)
- [H: Disk Information](#appendix-h-disk-information)

---

## 1. Some Introductory Remarks

### 1-1. Introduction

#### Conventions Used in This Manual

Throughout this manual, the following conventions are used to describe BASIC instructions:

- Items in CAPITAL LETTERS must be input as shown
- Items in `<angle brackets>` describe information to be supplied
- Items in `[square brackets]` are optional
- Items followed by `...` may be repeated one or more times
- Items separated by `|` are alternatives

#### Definitions

| Term | Definition |
|------|------------|
| Line | A string of characters followed by RETURN. BASIC adds a line number before storing |
| Direct Statement | A statement executed immediately (no line number) |
| Indirect Statement | A statement stored in memory (has line number) |
| Character | Any letter, digit, or special symbol |
| Alphanumeric | Letters A-Z and digits 0-9 |
| Expression | A formula using variables, constants, and operators |

### 1-2. Modes of Operation

Altair BASIC has two modes of operation:

**Direct Mode (Command Level)**
- Enter statements without line numbers
- Execute immediately after pressing RETURN
- BASIC prints `OK` when ready for input

**Indirect Mode (Program Level)**
- Enter statements with line numbers
- Statements are stored in memory
- Execute with the RUN command

### 1-3. Formats

#### Lines - AUTO and RENUM

A BASIC program consists of numbered lines. Line numbers range from 0 to 65529. Lines may contain multiple statements separated by colons (:).

**AUTO** - Automatic Line Numbering (Extended, Disk)
```basic
AUTO [<start>][,<increment>]
```
Example:
```basic
AUTO 100,10
```
Generates line numbers 100, 110, 120, etc. Press CTRL-C to cancel.

**RENUM** - Renumber Program Lines (Extended, Disk)
```basic
RENUM [<new>][,<old>][,<increment>]
```

#### REMarks

The REM statement allows comments in programs:
```basic
10 REM This is a comment
```
Everything after REM is ignored.

#### Error Messages

When BASIC detects an error, it prints a two-letter error code followed by "ERROR" and the line number (if in a program). For example:
```
SN ERROR IN 150
```
Means "Syntax Error in line 150".

### 1-4. Editing

#### Single Character Editing

| Key | Function |
|-----|----------|
| RUBOUT (DEL) | Delete previous character |
| CTRL-A | Re-enter line from start (Extended, Disk) |
| LINE FEED | Enter line but stay on current line number |

#### Line Editing

- To delete a line: Type its number and press RETURN
- To replace a line: Type new line with same number

**DELETE** - Delete a Range of Lines (Extended, Disk)
```basic
DELETE <start>-<end>
```

**EDIT** - Edit a Line (Extended, Disk)
```basic
EDIT <line number>
```

#### Control Characters

| Key | Function |
|-----|----------|
| CTRL-C | Stop program execution |
| CTRL-O | Toggle output suppression |
| CTRL-S | Pause output |
| CTRL-Q | Resume output |
| CTRL-I | Tab (8 spaces) |
| CTRL-U | Cancel current line (8K, Extended, Disk) |

---

## 2. Expressions and Statements

### 2-1. Expressions

#### Constants

**Integer Constants** (Extended, Disk)
- Whole numbers from -32768 to 32767
- Example: `42`, `-1000`

**Single Precision Constants**
- 6 significant digits
- Example: `3.14159`, `1.5E6`

**Double Precision Constants** (Extended, Disk)
- 16 significant digits
- Use D instead of E for exponent
- Example: `3.14159265358979D0`

**Hexadecimal Constants** (8K, Extended, Disk)
- Prefix with &H
- Example: `&HFF` (255 decimal)

**Octal Constants** (Extended, Disk)
- Prefix with &O
- Example: `&O377` (255 decimal)

#### Variables

**Variable Names**
- First character must be a letter
- Second character may be letter or digit
- Type suffix: `%` (integer), `!` (single), `#` (double), `$` (string)

Examples:
```basic
A%      ' integer
B!      ' single precision
C#      ' double precision
D$      ' string
```

**Type Declaration Statements** (Extended, Disk)
```basic
DEFINT A-Z      ' All variables default to integer
DEFSNG A-M      ' A-M default to single precision
DEFDBL N-Z      ' N-Z default to double precision
DEFSTR S        ' S defaults to string
```

#### Arrays - The DIM Statement

Arrays must be declared if they have more than 10 elements:
```basic
DIM A(100)          ' 101 elements (0-100)
DIM B(10,10)        ' 11x11 two-dimensional array
DIM C$(50)          ' String array
```

**ERASE** - Clear Arrays (Extended, Disk)
```basic
ERASE A,B,C$
```

#### Operators and Precedence

**Arithmetic Operators** (highest to lowest precedence):
| Operator | Operation |
|----------|-----------|
| `^` | Exponentiation |
| `-` | Negation (unary minus) |
| `*`, `/` | Multiplication, Division |
| `\` | Integer Division (8K, Extended, Disk) |
| `MOD` | Modulo (Extended, Disk) |
| `+`, `-` | Addition, Subtraction |

**Relational Operators**:
| Operator | Meaning |
|----------|---------|
| `=` | Equal |
| `<>` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

**Logical Operators** (lowest to highest):
| Operator | Function |
|----------|----------|
| `NOT` | Logical NOT |
| `AND` | Logical AND |
| `OR` | Logical OR |
| `XOR` | Exclusive OR (8K, Extended, Disk) |
| `IMP` | Implication (8K, Extended, Disk) |
| `EQV` | Equivalence (8K, Extended, Disk) |

#### The LET Statement

```basic
[LET] <variable> = <expression>
```
LET is optional. Both forms are equivalent:
```basic
LET X = 5
X = 5
```

### 2-2. Branching and Loops

#### GOTO - Unconditional Branch
```basic
GOTO <line number>
```

#### IF...THEN...ELSE - Conditional Branch
```basic
IF <expression> THEN <statement(s)> [ELSE <statement(s)>]
IF <expression> GOTO <line>
```
Examples:
```basic
10 IF X > 5 THEN PRINT "BIG"
20 IF A$ = "YES" THEN 100 ELSE 200
30 IF X GOTO 500
```

#### ON...GOTO and ON...GOSUB
```basic
ON <expression> GOTO <line1>,<line2>,...
ON <expression> GOSUB <line1>,<line2>,...
```
Example:
```basic
10 INPUT "CHOICE (1-3)"; C
20 ON C GOTO 100,200,300
```

#### FOR...NEXT Loops
```basic
FOR <variable> = <start> TO <end> [STEP <increment>]
    <statements>
NEXT [<variable>]
```
Example:
```basic
10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I
```

#### GOSUB...RETURN - Subroutines
```basic
GOSUB <line number>
...
RETURN
```
Example:
```basic
10 GOSUB 1000
20 END
1000 PRINT "SUBROUTINE"
1010 RETURN
```

### 2-3. Input/Output

#### INPUT Statement
```basic
INPUT ["<prompt>";] <variable list>
```
Examples:
```basic
INPUT X
INPUT "ENTER NAME"; N$
INPUT "VALUES"; A,B,C
```

#### LINE INPUT (Extended, Disk)
```basic
LINE INPUT ["<prompt string>";] <string variable>
```
Reads entire line including commas and quotes into string variable. LINE INPUT may not be edited by CTRL-A.

#### PRINT Statement
```basic
PRINT [<expression list>]
```
- Comma (,) tabs to next zone (14 columns)
- Semicolon (;) suppresses spacing
- No separator at end prints newline

Examples:
```basic
PRINT "HELLO"
PRINT A, B, C
PRINT X;Y;
PRINT TAB(20); "COLUMN 20"
PRINT USING "##.##"; 3.14159
```

#### PRINT USING - Formatted Output (8K, Extended, Disk)
```basic
PRINT USING "<format string>"; <expression list>
```

Format characters:
| Character | Meaning |
|-----------|---------|
| `#` | Digit position |
| `.` | Decimal point |
| `,` | Print comma every 3 digits |
| `+` | Print sign |
| `-` | Trailing minus for negative |
| `**` | Fill with asterisks |
| `$$` | Print dollar sign |
| `^^^^` | Exponential format |
| `!` | First character of string |
| `\  \` | n+2 characters of string |
| `&` | Entire string |

Examples:
```basic
PRINT USING "###.##"; 45.6        ' prints " 45.60"
PRINT USING "$###.##"; 12.5       ' prints " $12.50"
PRINT USING "**###.##"; 1.23      ' prints "***1.23"
```

#### DATA, READ, RESTORE
```basic
DATA <constant list>
READ <variable list>
RESTORE [<line number>]
```
Example:
```basic
10 DATA 1, 2, 3, "HELLO"
20 READ A, B, C, D$
30 RESTORE
40 READ X, Y
```

#### OUT and INP - Direct I/O (8K, Extended, Disk)
```basic
OUT <port>, <byte>
X = INP(<port>)
```

#### PEEK and POKE - Memory Access
```basic
X = PEEK(<address>)
POKE <address>, <byte>
```
If address is negative, actual address is 65536+address.

#### WAIT Statement
```basic
WAIT <port>, <mask>[, <xor>]
```
Waits until `(INP(port) XOR xor) AND mask` is nonzero.

---

## 3. Functions

### 3-1. Intrinsic Functions

#### Mathematical Functions

| Function | Description | Available |
|----------|-------------|-----------|
| `ABS(X)` | Absolute value | All |
| `SGN(X)` | Sign (-1, 0, or 1) | All |
| `INT(X)` | Largest integer <= X | All |
| `FIX(X)` | Truncate toward zero | Extended, Disk |
| `SQR(X)` | Square root | All (optional in 4K) |
| `EXP(X)` | e to the X power | 8K, Extended, Disk |
| `LOG(X)` | Natural logarithm | 8K, Extended, Disk |
| `SIN(X)` | Sine (radians) | All (optional in 4K) |
| `COS(X)` | Cosine | 8K, Extended, Disk |
| `TAN(X)` | Tangent | 8K, Extended, Disk |
| `ATN(X)` | Arctangent | 8K, Extended, Disk |
| `RND(X)` | Random number | All (optional in 4K) |

**RND Function:**
- `RND(0)` - Repeat last number
- `RND(X)` where X>0 - Next random number (0 to 1)
- `RND(X)` where X<0 - Reseed with X

#### Conversion Functions

| Function | Description | Available |
|----------|-------------|-----------|
| `CINT(X)` | Convert to integer | Extended, Disk |
| `CSNG(X)` | Convert to single | Extended, Disk |
| `CDBL(X)` | Convert to double | Extended, Disk |
| `HEX$(X)` | Convert to hex string | Extended, Disk |
| `OCT$(X)` | Convert to octal string | Extended, Disk |

#### Other Functions

| Function | Description | Available |
|----------|-------------|-----------|
| `POS(X)` | Current cursor column | All |
| `LPOS(X)` | Current printer column | Extended, Disk |
| `FRE(X)` | Free memory bytes | All |
| `SPC(X)` | Print X spaces | All |
| `TAB(X)` | Tab to column X | All |

### 3-2. User-Defined Functions

```basic
DEF FN<name>(<parameter>) = <expression>
```
Example:
```basic
10 DEF FNA(X) = X * X + 2 * X + 1
20 PRINT FNA(5)
```

Extended and Disk BASIC allow multi-line functions using DEF FN...END DEF.

### 3-3. The USR Function

```basic
X = USR(<argument>)
```

Calls a machine language subroutine. In 4K and 8K, the starting address is stored in USRLOC (111 octal). In Extended and Disk, use DEFUSR.

**DEFUSR** (Extended, Disk)
```basic
DEFUSR<n> = <address>
X = USR<n>(<argument>)
```
Where n is 0-9.

---

## 4. Strings

### 4-1. String Variables

String variables are denoted by a `$` suffix:
```basic
A$ = "HELLO"
NAME$ = "JOHN DOE"
```

Maximum string length is 255 characters.

### 4-2. String Operators

**Concatenation:**
```basic
A$ = "HELLO" + " " + "WORLD"
```

**Comparison:**
Strings can be compared using relational operators. Comparison is character by character using ASCII values.

### 4-3. String Functions

| Function | Description | Available |
|----------|-------------|-----------|
| `LEN(X$)` | Length of string | All |
| `LEFT$(X$,N)` | Leftmost N characters | All |
| `RIGHT$(X$,N)` | Rightmost N characters | All |
| `MID$(X$,P,N)` | N characters starting at P | All |
| `ASC(X$)` | ASCII code of first character | All |
| `CHR$(N)` | Character with ASCII code N | All |
| `VAL(X$)` | Numeric value of string | All |
| `STR$(N)` | String representation of N | All |
| `INSTR(S$,T$)` | Position of T$ in S$ | Extended, Disk |
| `STRING$(N,C)` | N copies of character C | Extended, Disk |
| `SPACE$(N)` | N spaces | Extended, Disk |

#### MID$ Assignment (Extended, Disk)

```basic
MID$(X$,P,N) = Y$
```
Replaces N characters of X$ starting at position P with Y$.

Example:
```basic
10 A$ = "HELLO WORLD"
20 MID$(A$,7,5) = "THERE"
30 PRINT A$
```
Prints: `HELLO THERE`

### 4-4. CLEAR Statement

```basic
CLEAR [<string space>]
```
Clears all variables. The optional parameter sets string space (see Memory Management).

---

## 5. Extended Features

### 5-1. Error Trapping (Extended, Disk)

```basic
ON ERROR GOTO <line>
```
Enables error trapping. When an error occurs, execution continues at the specified line.

```basic
RESUME [<line>|NEXT]
```
- `RESUME` - Retry the statement that caused the error
- `RESUME NEXT` - Continue with the statement after the error
- `RESUME <line>` - Continue at specified line

**Error Information:**
- `ERR` - Error code number
- `ERL` - Line number where error occurred
- `ERROR <n>` - Generate error n

Example:
```basic
10 ON ERROR GOTO 1000
20 OPEN "I", #1, "NOFILE"
30 END
1000 IF ERR = 53 THEN PRINT "FILE NOT FOUND"
1010 RESUME NEXT
```

### 5-2. SWAP Statement (Extended, Disk)

```basic
SWAP <variable1>, <variable2>
```
Exchanges values of two variables of the same type.

### 5-3. Program Flow Control (Extended, Disk)

**WHILE...WEND**
```basic
WHILE <condition>
    <statements>
WEND
```

### 5-4. Line Printer Output (Extended, Disk)

```basic
LPRINT <expression list>
LPRINT USING "<format>"; <expression list>
```

**WIDTH** - Set Line Width
```basic
WIDTH <columns>
WIDTH LPRINT <columns>
```

### 5-5. CONSOLE Statement (8K, Extended, Disk)

```basic
CONSOLE <board number>
```
Selects the I/O board for terminal communication. Retained when answering "C" (in Extended and Disk) to the SIN-COS-TAN-ATN question at initialization.

### 5-6. NULL Statement

```basic
NULL <count>
```
Sets the number of null characters output after each carriage return (for slow terminals like teletypes).

### 5-7. Disk File Operations (Disk Version)

#### Opening Files

**Sequential Files:**
```basic
OPEN "I", #<n>, "<filename>"     ' Input
OPEN "O", #<n>, "<filename>"     ' Output
OPEN "A", #<n>, "<filename>"     ' Append (Extended, Disk)
```

**Random Files:**
```basic
OPEN "R", #<n>, "<filename>"[,<drive>]
```

#### File I/O

**Sequential Read:**
```basic
INPUT #<n>, <variable list>
LINE INPUT #<n>, <string variable>
```

**Sequential Write:**
```basic
PRINT #<n>, <expression list>
```

**Random File Fields:**
```basic
FIELD #<n>, <width> AS <variable>,...
```

**Random File Access:**
```basic
GET #<n>, <record number>
PUT #<n>, <record number>
```

**Field Conversion Functions:**
```basic
MKI$(<integer>)      ' Make integer field string
MKS$(<single>)       ' Make single field string
MKD$(<double>)       ' Make double field string
CVI(<string>)        ' Convert to integer
CVS(<string>)        ' Convert to single
CVD(<string>)        ' Convert to double
```

#### Closing Files

```basic
CLOSE <n>
CLOSE              ' Close all files
```

#### File Management

```basic
KILL "<filename>"              ' Delete file
NAME "<old>" AS "<new>"        ' Rename file
FILES [<drive>]                ' List directory
MOUNT <drive>                  ' Mount disk
UNLOAD <drive>                 ' Unload disk
```

#### Disk Functions

| Function | Description |
|----------|-------------|
| `LOC(n)` | Current position in file |
| `LOF(n)` | Length of file |
| `EOF(n)` | End of file flag |
| `DSKF(n)` | Free space on disk |

### 5-8. TRON and TROFF (8K, Extended, Disk)

```basic
TRON              ' Enable trace
TROFF             ' Disable trace
```
When trace is on, line numbers are printed in brackets as they execute.

---

## 6. Quick Reference

### Commands

| Command | Description | Available |
|---------|-------------|-----------|
| `AUTO` | Auto line numbering | Extended, Disk |
| `CLEAR` | Clear variables | All |
| `CLOAD` | Load from cassette | 8K |
| `CLOAD*` | Load array from cassette | 8K, Extended, Disk |
| `CONT` | Continue after stop | All |
| `CSAVE` | Save to cassette | 8K |
| `CSAVE*` | Save array to cassette | 8K, Extended, Disk |
| `DELETE` | Delete lines | Extended, Disk |
| `EDIT` | Edit a line | Extended, Disk |
| `FILES` | List disk files | Disk |
| `KILL` | Delete disk file | Disk |
| `LIST` | List program | All |
| `LLIST` | List to printer | Extended, Disk |
| `LOAD` | Load from disk | Disk |
| `MERGE` | Merge program | Disk |
| `MOUNT` | Mount disk | Disk |
| `NAME` | Rename file | Disk |
| `NEW` | Clear program | All |
| `NULL` | Set null count | All |
| `RENUM` | Renumber lines | Extended, Disk |
| `RUN` | Execute program | All |
| `SAVE` | Save to disk | Disk |
| `TRON/TROFF` | Trace on/off | 8K, Extended, Disk |
| `UNLOAD` | Unload disk | Disk |
| `WIDTH` | Set line width | Extended, Disk |

### Statements

| Statement | Description | Available |
|-----------|-------------|-----------|
| `CLOSE` | Close file | Disk |
| `DATA` | Define data | All |
| `DEF FN` | Define function | All |
| `DEFINT/SNG/DBL/STR` | Type defaults | Extended, Disk |
| `DEFUSR` | Define USR address | Extended, Disk |
| `DIM` | Dimension array | All |
| `END` | End program | All |
| `ERASE` | Erase array | Extended, Disk |
| `ERROR` | Generate error | Extended, Disk |
| `FIELD` | Define random buffer | Disk |
| `FOR...NEXT` | Loop | All |
| `GET` | Read random record | Disk |
| `GOSUB` | Call subroutine | All |
| `GOTO` | Branch | All |
| `IF...THEN...ELSE` | Conditional | All (ELSE: Ext, Disk) |
| `INPUT` | Read input | All |
| `INPUT #` | Read from file | Disk |
| `LET` | Assignment | All |
| `LINE INPUT` | Read line | Extended, Disk |
| `LPRINT` | Print to printer | Extended, Disk |
| `LSET/RSET` | Set field data | Disk |
| `ON ERROR` | Error trap | Extended, Disk |
| `ON...GOTO/GOSUB` | Computed branch | All |
| `OPEN` | Open file | Disk |
| `OUT` | Output to port | 8K, Extended, Disk |
| `POKE` | Write to memory | All |
| `PRINT` | Output | All |
| `PRINT #` | Write to file | Disk |
| `PRINT USING` | Formatted output | 8K, Extended, Disk |
| `PUT` | Write random record | Disk |
| `READ` | Read DATA | All |
| `REM` | Comment | All |
| `RESTORE` | Reset DATA pointer | All |
| `RESUME` | Resume after error | Extended, Disk |
| `RETURN` | Return from subroutine | All |
| `STOP` | Stop execution | All |
| `SWAP` | Exchange variables | Extended, Disk |
| `WAIT` | Wait for port | All |
| `WHILE...WEND` | While loop | Extended, Disk |

### Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| BS | Bad Subscript | Array index out of range |
| DD | Double Dimension | Array already dimensioned |
| FC | Function Call | Illegal function argument |
| ID | Illegal Direct | Statement not allowed in direct mode |
| NF | NEXT without FOR | NEXT without matching FOR |
| OD | Out of Data | READ with no DATA left |
| OV | Overflow | Number too large |
| OM | Out of Memory | Program too large |
| RG | RETURN without GOSUB | RETURN without GOSUB |
| SN | Syntax | Invalid statement |
| ST | String Too long | String exceeds 255 characters |
| TM | Type Mismatch | Wrong variable type |
| UL | Undefined Line | GOTO/GOSUB to nonexistent line |

**Disk Errors:**
| Code | Message |
|------|---------|
| AO | File Already Open |
| BN | Bad Number |
| CF | Close File |
| CN | Can't Continue |
| DF | Disk Full |
| DS | Disk I/O Error |
| FF | File Found |
| FL | File Locked |
| NM | Not Mounted |
| FN | Bad File Number |

---

## Appendix A: ASCII Character Codes

| Dec | Hex | Char | Dec | Hex | Char | Dec | Hex | Char |
|-----|-----|------|-----|-----|------|-----|-----|------|
| 0 | 00 | NUL | 32 | 20 | SPACE | 64 | 40 | @ |
| 1 | 01 | SOH | 33 | 21 | ! | 65 | 41 | A |
| 2 | 02 | STX | 34 | 22 | " | 66 | 42 | B |
| 3 | 03 | ETX | 35 | 23 | # | 67 | 43 | C |
| 4 | 04 | EOT | 36 | 24 | $ | 68 | 44 | D |
| 5 | 05 | ENQ | 37 | 25 | % | 69 | 45 | E |
| 6 | 06 | ACK | 38 | 26 | & | 70 | 46 | F |
| 7 | 07 | BEL | 39 | 27 | ' | 71 | 47 | G |
| 8 | 08 | BS | 40 | 28 | ( | 72 | 48 | H |
| 9 | 09 | TAB | 41 | 29 | ) | 73 | 49 | I |
| 10 | 0A | LF | 42 | 2A | * | 74 | 4A | J |
| 11 | 0B | VT | 43 | 2B | + | 75 | 4B | K |
| 12 | 0C | FF | 44 | 2C | , | 76 | 4C | L |
| 13 | 0D | CR | 45 | 2D | - | 77 | 4D | M |
| 14 | 0E | SO | 46 | 2E | . | 78 | 4E | N |
| 15 | 0F | SI | 47 | 2F | / | 79 | 4F | O |
| 16 | 10 | DLE | 48 | 30 | 0 | 80 | 50 | P |
| 17 | 11 | DC1 | 49 | 31 | 1 | 81 | 51 | Q |
| 18 | 12 | DC2 | 50 | 32 | 2 | 82 | 52 | R |
| 19 | 13 | DC3 | 51 | 33 | 3 | 83 | 53 | S |
| 20 | 14 | DC4 | 52 | 34 | 4 | 84 | 54 | T |
| 21 | 15 | NAK | 53 | 35 | 5 | 85 | 55 | U |
| 22 | 16 | SYN | 54 | 36 | 6 | 86 | 56 | V |
| 23 | 17 | ETB | 55 | 37 | 7 | 87 | 57 | W |
| 24 | 18 | CAN | 56 | 38 | 8 | 88 | 58 | X |
| 25 | 19 | EM | 57 | 39 | 9 | 89 | 59 | Y |
| 26 | 1A | SUB | 58 | 3A | : | 90 | 5A | Z |
| 27 | 1B | ESC | 59 | 3B | ; | 91 | 5B | [ |
| 28 | 1C | FS | 60 | 3C | < | 92 | 5C | \ |
| 29 | 1D | GS | 61 | 3D | = | 93 | 5D | ] |
| 30 | 1E | RS | 62 | 3E | > | 94 | 5E | ^ |
| 31 | 1F | US | 63 | 3F | ? | 95 | 5F | _ |

---

## Appendix B: Loading BASIC

### Sense Switch Settings

Before loading BASIC from paper tape or cassette, set the sense switches (A8-A15) based on your terminal and load device:

| Device | Setting | Terminal Switches | Load Switches |
|--------|---------|-------------------|---------------|
| 2SIO (2 stop bits) | 0 | none | none |
| 2SIO (1 stop bit) | 1 | A12 | A8 |
| SIO | 2 | A13 | A9 |
| ACR (cassette) | 3 | A13,A12 | A9,A8 |
| 4PIO | 4 | A14 | A10 |
| PIO | 5 | A14,A12 | A10,A8 |
| HSR | 6 | A14,A13 | A10,A9 |

### Loading Procedure

1. Toggle in the appropriate bootstrap loader
2. Position tape/cassette at leader
3. Set sense switches for terminal and load device
4. Press RUN

### Error Codes During Load

| Code | Meaning |
|------|---------|
| C | Checksum error - bad tape data |
| M | Memory error - data won't store |
| O | Overlay error - loading over loader |
| I | Invalid load device setting |

### Initialization Dialog

When BASIC loads, it asks:

```
MEMORY SIZE?
```
Press RETURN to auto-detect, or enter maximum address.

```
TERMINAL WIDTH?
```
Enter line width (default 72).

**4K BASIC also asks:**
```
SIN?       ' Y to keep SIN, SQR, RND
SQR?       ' Y to keep SQR, RND
RND?       ' Y to keep RND
```

**8K and Extended ask:**
```
WANT SIN-COS-TAN-ATN?
```
- Y - Keep all trig functions
- N - Delete all
- C - (Extended and Disk) Keep all functions including CONSOLE

After initialization:
```
XXXXX BYTES FREE
ALTAIR BASIC REV. 4.0
[FOUR-K VERSION] / [EIGHT-K VERSION] / [EXTENDED VERSION]
COPYRIGHT 1976 BY MITS INC.
OK
```

---

## Appendix C: Space and Speed Hints

### Space Allocation

| Element | Space Required |
|---------|----------------|
| **Variables:** | |
| Integer | 5 bytes |
| Single precision | 6 bytes (4K, 8K) / 7 bytes (Extended, Disk) |
| Double precision | 11 bytes |
| String | 6 bytes |
| **Arrays:** | |
| Integer | (elements * 2) + 6 + (dimensions * 2) bytes |
| Single precision | (elements * 4) + 6 + (dimensions * 2) bytes |
| Double precision | (elements * 8) + 6 + (dimensions * 2) bytes |
| **Other:** | |
| Reserved words | 1 byte each (2 for ELSE) |
| Active FOR loop | 16 bytes (4K, 8K) / 17 bytes (Extended, Disk) |
| Active GOSUB | 5 bytes |
| Parentheses | 6 bytes per set |

**BASIC Interpreter Size:**
- 4K: ~3.4K
- 8K: ~6.2K
- Extended: ~14.6K
- Disk: ~29K

### Space Hints

1. Use multiple statements per line (saves 5 bytes per line)
2. Delete unnecessary spaces: `10 PRINTX,Y,Z` instead of `10 PRINT X, Y, Z`
3. Delete REM statements
4. Use variables for repeated constants
5. Don't use END as the last statement
6. Reuse variables
7. Use subroutines instead of duplicate code
8. Use the smallest BASIC version that works
9. Use array element 0 (DIM A(10) gives 11 elements)
10. Use integer variables where possible (Extended, Disk)

### Speed Hints

1. Delete spaces and REMs
2. Put frequently-used variables first (faster lookup)
3. Use NEXT without variable name (8K, Extended, Disk)
4. 8K and Extended have faster floating point than 4K
5. Use variables instead of constants in loops
6. Use integer variables (Extended, Disk)

---

## Appendix D: Mathematical Functions

### Derived Functions

These functions can be calculated from built-in functions:

| Function | BASIC Equivalent |
|----------|------------------|
| Secant | `SEC(X) = 1/COS(X)` |
| Cosecant | `CSC(X) = 1/SIN(X)` |
| Cotangent | `COT(X) = 1/TAN(X)` |
| Inverse Sine | `ARCSIN(X) = ATN(X/SQR(-X*X+1))` |
| Inverse Cosine | `ARCCOS(X) = -ATN(X/SQR(-X*X+1))+1.5708` |
| Hyperbolic Sine | `SINH(X) = (EXP(X)-EXP(-X))/2` |
| Hyperbolic Cosine | `COSH(X) = (EXP(X)+EXP(-X))/2` |
| Hyperbolic Tangent | `TANH(X) = -EXP(-X)/(EXP(X)+EXP(-X))*2+1` |

### Simulated Functions for 4K BASIC

These subroutines implement functions not built into 4K BASIC:

```basic
60000 REM EXPONENTIATION: P9=X9^Y9
60010 REM NEED: EXP, LOG
60030 P9=1:E9=0:IF Y9=0 THEN RETURN
60040 IF X9<0 THEN IF INT(Y9)=Y9 THEN P9=1-2*Y9+4*INT(Y9/2):X9=-X9
60050 IF X9<>0 THEN GOSUB 60090:X9=Y9*L9:GOSUB 60160
60060 P9=P9*E9:RETURN

60070 REM NATURAL LOGARITHM: L9=LOG(X9)
60090 E9=0:IF X9<=0 THEN PRINT "LOG FC ERROR":STOP
60100 A9=1:B9=2:C9=.5
60110 IF X9>=A9 THEN X9=C9*X9:E9=E9+A9:GOTO 60110
60120 X9=(X9-.707107)/(X9+.707107):L9=X9*X9
60130 L9=(((.598979*L9+.961471)*L9+2.88539)*X9+E9-.5)*.693147
60135 RETURN

60140 REM EXPONENTIAL: E9=EXP(X9)
60160 L9=INT(1.4427*X9)+1:IF L9<127 THEN 60180
60170 IF X9>0 THEN PRINT "EXP OV ERROR":STOP
60175 E9=0:RETURN
60180 E9=.693147*L9-X9:A9=1.32988E-3-1.41316E-4*E9
60190 A9=((A9*E9-8.36136E-3)*E9+4.16574E-2)*E9
60195 E9=((A9-.166665)*E9-1)*E9+1:A9=2
60197 IF L9<=0 THEN A9=.5:L9=-L9:IF L9=0 THEN RETURN
60200 FOR X9=1 TO L9:E9=A9*E9:NEXT X9:RETURN

60210 REM COSINE: C9=COS(X9)
60220 REM N.B. SIN MUST BE RETAINED AT LOAD-TIME
60240 C9=SIN(X9+1.5708):RETURN

60250 REM TANGENT: T9=TAN(X9)
60260 REM NEEDS COS (SIN MUST BE RETAINED AT LOAD-TIME)
60280 GOSUB 60240:T9=SIN(X9)/C9:RETURN

60290 REM ARCTANGENT: A9=ATN(X9)
60310 T9=SGN(X9):X9=ABS(X9):C9=0:IF X9>1 THEN C9=1:X9=1/X9
60320 A9=X9*X9:B9=((2.86623E-3*A9-1.61657E-2)*A9+4.29096E-2)*A9
60330 B9=((((B9-7.5289E-2)*A9+.106563)*A9-.142089)*A9+.199936)*A9
60340 A9=((B9-.333332)*A9+1)*X9:IF C9=1 THEN A9=1.5708-A9
60350 A9=T9*A9:RETURN
```

---

## Appendix E: BASIC and Assembly Language

### USR Function

All versions of Altair BASIC can call assembly language routines via the USR function.

**Setting Up Memory:**

When BASIC asks "MEMORY SIZE?", reserve space for your routine by specifying a smaller memory size. Assembly routines must be at the top of memory (BASIC uses memory from 0 upward).

**USRLOC:**

The starting address of your routine goes in USRLOC:
- 4K and 8K version 4.0: **111 octal** (73 decimal)
- Extended and Disk: Use DEFUSR

**Stack:**

USR provides 8 levels (16 bytes) of stack space. Save BASIC's stack if you need more.

**Arguments:**

In 4K and 8K, call the routine at address stored in locations 4,5 (decimal) to get the argument in [D,E] as a signed 16-bit integer (-32768 to 32767).

In Extended, [H,L] points to the Floating Point Accumulator.

**Return Value:**

Load result in [A,B] (4K/8K) or [H,L] (Extended), then call the routine at address in locations 6,7 to return a signed 16-bit integer. Execute RET to return to BASIC.

**Interrupts:**

Locations 56, 57, 58 hold a JMP to user interrupt handler. Location 56 initially contains RET. Save all registers and PSW in interrupt handlers, and re-enable interrupts before returning.

---

## Appendix F: Using the ACR Interface

The cassette features (CLOAD and CSAVE) are in 8K cassette BASIC and Extended/Disk versions.

**CSAVE** - Save Program to Cassette
```basic
CSAVE "<name>"
```
The program is saved under the name specified by the first character of the string expression. Before using CSAVE, turn on the cassette recorder and put it in RECORD mode.

**CLOAD** - Load Program from Cassette
```basic
CLOAD "<name>"
```
Clears memory and loads the specified file. Reading continues until 3 consecutive zeros are read.

**CLOAD?** - Verify Program
```basic
CLOAD? "<name>"
```
Compares program in memory with tape. Prints "OK" if match, "NO GOOD" if not.

**CSAVE*** and **CLOAD*** - Array Data (8K cassette, Extended, Disk)
```basic
CSAVE*<array name>
CLOAD*<array name>
```

**Manual Cassette I/O (8K paper tape version):**

Write data:
```basic
WAIT 6,128       ' Wait for Write Buffer Empty
OUT 7,<byte>     ' Write byte
```

Read data:
```basic
WAIT 6,1         ' Wait for Read Data Ready
X = INP(7)       ' Read byte
```

---

## Appendix G: Converting BASIC Programs

### String Differences

Some BASICs require string length declarations. Remove these DIM statements. Convert substring notation:

| Old | New |
|-----|-----|
| `A$(I)` | `MID$(A$,I,1)` |
| `A$(I,J)` | `MID$(A$,I,J-I+1)` |

For assignments in Extended and Disk:
```basic
MID$(A$,I,1) = X$
MID$(A$,I,J-I+1) = X$
```

### Multiple Assignments

Some BASICs allow `LET B=C=0`. In Altair BASIC, the second `=` is a comparison operator. Convert to:
```basic
C=0:B=C
```

### Statement Separators

Change `\` to `:` for multiple statements on a line.

### Paper Tape Format

Other BASICs may not include nulls after carriage returns. Control tape manually or convert using a conversion program.

### MAT Functions

Programs using MAT functions must be rewritten using FOR...NEXT loops.

---

## Appendix H: Disk Information

### Disk Format

| Tracks | Use |
|--------|-----|
| 0-5 | Disk BASIC memory image |
| 6-69 | Random or sequential files |
| 70 | Directory track |
| 71-76 | Sequential files only |

### Sector Format (Tracks 6-76)

| Byte | Contents |
|------|----------|
| 0 | Track number + 240 octal |
| 1 | Sector number * 17 MOD 32 |
| 2 | File number in directory (0 = free) |
| 3 | Number of data bytes (0-128) |
| 4 | Checksum |
| 5-6 | Pointer to next group |
| 7-134 | Data |
| 135 | 255 (377 octal) stop byte |

### Directory Format (Track 70)

Each sector contains up to 8 file name slots (16 bytes each):
- 8 bytes: Filename
- 2 bytes: Link to start of file
- 1 byte: Mode (4=Random, 2=Sequential)
- 5 bytes: Reserved

File numbers are calculated by multiplying the sector number by 8 and adding the position of the slot (0-7) plus 1.

### Disk BASIC Initialization

```
MEMORY SIZE?            ' Press RETURN for auto-detect
HIGHEST DISK NUMBER?    ' Number of drives - 1
HOW MANY FILES?         ' Number of open files (138 bytes each)
HOW MANY RANDOM FILES?  ' Random files (395 bytes each)
```

### PIP Utility Commands

| Command | Function |
|---------|----------|
| `INI<n>` | Initialize disk in drive n |
| `DIR<n>` | Print directory |
| `SRT<n>` | Sorted directory |
| `LIS<n>,<file>` | List sequential file contents |
| `COP<n>,<m>` | Copy disk n to disk m |
| `DAT<n>` | Dump sector in octal |
| `CNV<n>` | Convert from version 3.x format |

---

## Index

| Term | Section |
|------|---------|
| ABS | 3-1 |
| ACR interface | Appendix F |
| AND | 2-1 |
| Array variables | 2-1 |
| ASC | 4-3 |
| ATN | 3-1 |
| AUTO | 1-3 |
| BASIC texts | Appendix J |
| Boot loaders | Appendix B |
| CHR$ | 4-3 |
| CLEAR | 4-4 |
| CLOAD | Appendix F |
| CLOSE | 5-7 |
| CONSOLE | 5-5 |
| Constants | 2-1 |
| CONT | 6 |
| Control characters | 1-4 |
| COS | 3-1 |
| CSAVE | Appendix F |
| CVD/CVI/CVS | 5-7 |
| DATA | 2-3 |
| DEF | 3-2 |
| DELETE | 1-4 |
| DIM | 2-1 |
| Disk format | Appendix H |
| EDIT | 1-4 |
| END | 6 |
| EOF | 5-7 |
| ERASE | 2-1 |
| ERR/ERL | 5-1 |
| Error codes | 6 |
| EXP | 3-1 |
| FIELD | 5-7 |
| FIX | 3-1 |
| FOR...NEXT | 2-2 |
| FRE | 3-1 |
| Functions | 3 |
| GET | 5-7 |
| GOSUB | 2-2 |
| GOTO | 2-2 |
| HEX$ | 3-1 |
| IF...THEN...ELSE | 2-2 |
| IMP | 2-1 |
| INP | 2-3 |
| INPUT | 2-3 |
| INSTR | 4-3 |
| INT | 3-1 |
| KILL | 5-7 |
| LEFT$ | 4-3 |
| LEN | 4-3 |
| LET | 2-1 |
| LINE INPUT | 2-3 |
| LIST | 6 |
| LOAD | 5-7 |
| LOC | 5-7 |
| LOG | 3-1 |
| LPRINT | 5-4 |
| LSET/RSET | 5-7 |
| MERGE | 5-7 |
| MID$ | 4-3 |
| MKD$/MKI$/MKS$ | 5-7 |
| MOD | 2-1 |
| MOUNT | 5-7 |
| NAME | 5-7 |
| NEW | 6 |
| NEXT | 2-2 |
| NOT | 2-1 |
| NULL | 5-6 |
| OCT$ | 3-1 |
| ON ERROR | 5-1 |
| ON...GOSUB/GOTO | 2-2 |
| OPEN | 5-7 |
| Operators | 2-1 |
| OR | 2-1 |
| OUT | 2-3 |
| PEEK | 2-3 |
| PIP utility | Appendix H |
| POKE | 2-3 |
| POS | 3-1 |
| PRINT | 2-3 |
| PRINT USING | 2-3 |
| PUT | 5-7 |
| Random files | 5-7 |
| READ | 2-3 |
| REM | 1-3 |
| RENUM | 1-3 |
| Reserved words | 6 |
| RESTORE | 2-3 |
| RESUME | 5-1 |
| RETURN | 2-2 |
| RIGHT$ | 4-3 |
| RND | 3-1 |
| RUN | 6 |
| SAVE | 5-7 |
| Sense switches | Appendix B |
| Sequential files | 5-7 |
| SGN | 3-1 |
| SIN | 3-1 |
| Space hints | Appendix C |
| SPACE$ | 4-3 |
| SPC | 3-1 |
| Speed hints | Appendix C |
| SQR | 3-1 |
| STOP | 6 |
| STR$ | 4-3 |
| STRING$ | 4-3 |
| Strings | 4 |
| SWAP | 5-2 |
| TAB | 3-1 |
| TAN | 3-1 |
| TRON/TROFF | 5-8 |
| UNLOAD | 5-7 |
| USR | 3-3 |
| VAL | 4-3 |
| Variables | 2-1 |
| VARPTR | 6 |
| WAIT | 2-3 |
| WHILE...WEND | 5-3 |
| WIDTH | 5-4 |
| XOR | 2-1 |
