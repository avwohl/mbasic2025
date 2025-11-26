"""
Microsoft REL relocatable object file format for um80/ul80.

REL files are bit streams. Items are NOT byte-aligned.

Bit patterns:
- 0 + 8 bits: Absolute byte to load
- 1 00: Special LINK item
- 1 01 + 16 bits: Program relative (add to code segment base)
- 1 10 + 16 bits: Data relative (add to data segment base)
- 1 11 + 16 bits: Common relative (add to common base)

Special LINK items (100 + 4-bit control):
Control  A-field  B-field  Meaning
0        -        B        Entry symbol (for library search)
1        -        B        Select COMMON block
2        -        B        Program name
3        -        B        Request library search
4        -        -        (reserved)
5        A        B        Define COMMON size
6        A        B        Chain external (A=head, B=name)
7        A        B        Define entry point (A=addr, B=name)
8        A        B        External-offset (for JMP/CALL to external)
9        A        -        External + offset (add A to current loc)
10       A        -        Define Data area size
11       A        -        Set location counter
12       A        -        Chain address (A=head of chain)
13       A        -        Define program size
14       -        -        End program (force byte boundary)
15       -        -        End file

A-field: 2-bit address type + 16-bit value
  00 = absolute
  01 = program relative
  10 = data relative
  11 = common relative

B-field: 3-bit length (0-7, but 0 means 8 chars) + 8 bits per character
"""

class BitWriter:
    """Write bits to a byte stream."""

    def __init__(self):
        self.bytes = bytearray()
        self.current_byte = 0
        self.bit_pos = 0  # 0-7, next bit to write (MSB first)

    def write_bit(self, bit):
        """Write a single bit (0 or 1)."""
        if bit:
            self.current_byte |= (0x80 >> self.bit_pos)
        self.bit_pos += 1
        if self.bit_pos == 8:
            self.bytes.append(self.current_byte)
            self.current_byte = 0
            self.bit_pos = 0

    def write_bits(self, value, count):
        """Write 'count' bits from value (MSB first)."""
        for i in range(count - 1, -1, -1):
            self.write_bit((value >> i) & 1)

    def write_byte(self, value):
        """Write 8 bits."""
        self.write_bits(value & 0xFF, 8)

    def write_word(self, value):
        """Write 16 bits (low byte first, as per 8080 convention)."""
        self.write_byte(value & 0xFF)
        self.write_byte((value >> 8) & 0xFF)

    def force_byte_boundary(self):
        """Pad to next byte boundary."""
        if self.bit_pos != 0:
            self.bytes.append(self.current_byte)
            self.current_byte = 0
            self.bit_pos = 0

    def get_bytes(self):
        """Get the byte array, padding if necessary."""
        result = bytearray(self.bytes)
        if self.bit_pos != 0:
            result.append(self.current_byte)
        return bytes(result)


class BitReader:
    """Read bits from a byte stream."""

    def __init__(self, data):
        self.data = data
        self.byte_pos = 0
        self.bit_pos = 0  # 0-7, next bit to read (MSB first)

    def read_bit(self):
        """Read a single bit."""
        if self.byte_pos >= len(self.data):
            raise EOFError("End of REL file")
        bit = (self.data[self.byte_pos] >> (7 - self.bit_pos)) & 1
        self.bit_pos += 1
        if self.bit_pos == 8:
            self.byte_pos += 1
            self.bit_pos = 0
        return bit

    def read_bits(self, count):
        """Read 'count' bits and return as integer."""
        value = 0
        for _ in range(count):
            value = (value << 1) | self.read_bit()
        return value

    def read_byte(self):
        """Read 8 bits."""
        return self.read_bits(8)

    def read_word(self):
        """Read 16 bits (low byte first)."""
        low = self.read_byte()
        high = self.read_byte()
        return low | (high << 8)

    def at_end(self):
        """Check if at end of data."""
        return self.byte_pos >= len(self.data)

    def force_byte_boundary(self):
        """Skip to next byte boundary."""
        if self.bit_pos != 0:
            self.byte_pos += 1
            self.bit_pos = 0


# Address type constants
ADDR_ABSOLUTE = 0
ADDR_PROGRAM_REL = 1
ADDR_DATA_REL = 2
ADDR_COMMON_REL = 3

# Special link item types
LINK_ENTRY_SYMBOL = 0
LINK_SELECT_COMMON = 1
LINK_PROGRAM_NAME = 2
LINK_REQUEST_LIB = 3
LINK_RESERVED = 4
LINK_DEFINE_COMMON_SIZE = 5
LINK_CHAIN_EXTERNAL = 6
LINK_DEFINE_ENTRY = 7
LINK_EXTERNAL_OFFSET = 8
LINK_EXTERNAL_PLUS_OFFSET = 9
LINK_DEFINE_DATA_SIZE = 10
LINK_SET_LOC = 11
LINK_CHAIN_ADDRESS = 12
LINK_DEFINE_PROG_SIZE = 13
LINK_END_PROGRAM = 14
LINK_END_FILE = 15


class RELWriter:
    """Write Microsoft REL format relocatable object files."""

    def __init__(self):
        self.bits = BitWriter()

    def write_absolute_byte(self, value):
        """Write an absolute byte (0 + 8 bits)."""
        self.bits.write_bit(0)
        self.bits.write_byte(value)

    def write_program_relative(self, value):
        """Write program-relative 16-bit value."""
        self.bits.write_bits(0b101, 3)  # 1 01
        self.bits.write_word(value)

    def write_data_relative(self, value):
        """Write data-relative 16-bit value."""
        self.bits.write_bits(0b110, 3)  # 1 10
        self.bits.write_word(value)

    def write_common_relative(self, value):
        """Write common-relative 16-bit value."""
        self.bits.write_bits(0b111, 3)  # 1 11
        self.bits.write_word(value)

    def _write_a_field(self, addr_type, value):
        """Write A-field: 2-bit type + 16-bit value."""
        self.bits.write_bits(addr_type, 2)
        self.bits.write_word(value)

    def _write_b_field(self, name):
        """Write B-field: 3-bit length + characters."""
        # Only first 6 chars significant per M80 spec, but we store up to 8
        name = name.upper()[:8]
        length = len(name)
        if length == 8:
            length = 0  # 0 means 8 characters
        self.bits.write_bits(length, 3)
        for ch in name:
            self.bits.write_byte(ord(ch))

    def _write_special(self, control, a_field=None, b_field=None):
        """Write a special LINK item."""
        self.bits.write_bits(0b100, 3)  # 1 00
        self.bits.write_bits(control, 4)
        if a_field is not None:
            addr_type, value = a_field
            self._write_a_field(addr_type, value)
        if b_field is not None:
            self._write_b_field(b_field)

    def write_entry_symbol(self, name):
        """Entry symbol for library search."""
        self._write_special(LINK_ENTRY_SYMBOL, b_field=name)

    def write_select_common(self, name):
        """Select COMMON block."""
        self._write_special(LINK_SELECT_COMMON, b_field=name)

    def write_program_name(self, name):
        """Set program/module name."""
        self._write_special(LINK_PROGRAM_NAME, b_field=name)

    def write_request_library(self, name):
        """Request library search (.REQUEST)."""
        self._write_special(LINK_REQUEST_LIB, b_field=name)

    def write_define_common_size(self, addr_type, size, name):
        """Define COMMON block size."""
        self._write_special(LINK_DEFINE_COMMON_SIZE,
                          a_field=(addr_type, size), b_field=name)

    def write_chain_external(self, addr_type, head, name):
        """Chain external reference."""
        self._write_special(LINK_CHAIN_EXTERNAL,
                          a_field=(addr_type, head), b_field=name)

    def write_define_entry_point(self, addr_type, addr, name):
        """Define entry point (PUBLIC symbol)."""
        self._write_special(LINK_DEFINE_ENTRY,
                          a_field=(addr_type, addr), b_field=name)

    def write_external_offset(self, addr_type, offset, name):
        """External with offset (for JMP/CALL to external)."""
        self._write_special(LINK_EXTERNAL_OFFSET,
                          a_field=(addr_type, offset), b_field=name)

    def write_external_plus_offset(self, addr_type, offset):
        """Add offset to external at current location."""
        self._write_special(LINK_EXTERNAL_PLUS_OFFSET,
                          a_field=(addr_type, offset))

    def write_define_data_size(self, size):
        """Define data segment size."""
        self._write_special(LINK_DEFINE_DATA_SIZE,
                          a_field=(ADDR_ABSOLUTE, size))

    def write_set_location(self, addr_type, addr):
        """Set location counter."""
        self._write_special(LINK_SET_LOC,
                          a_field=(addr_type, addr))

    def write_chain_address(self, addr_type, head):
        """Chain address - fill chain with current location."""
        self._write_special(LINK_CHAIN_ADDRESS,
                          a_field=(addr_type, head))

    def write_define_program_size(self, size):
        """Define program (code) segment size."""
        self._write_special(LINK_DEFINE_PROG_SIZE,
                          a_field=(ADDR_ABSOLUTE, size))

    def write_end_program(self, entry_addr=None, entry_type=ADDR_ABSOLUTE):
        """End of program, optional entry address."""
        if entry_addr is not None:
            # Write entry address before end
            self._write_special(LINK_SET_LOC,
                              a_field=(entry_type, entry_addr))
        self._write_special(LINK_END_PROGRAM)
        self.bits.force_byte_boundary()

    def write_end_file(self):
        """End of file marker."""
        self._write_special(LINK_END_FILE)
        self.bits.force_byte_boundary()

    def get_bytes(self):
        """Get the REL file content."""
        return self.bits.get_bytes()


class RELReader:
    """Read Microsoft REL format relocatable object files."""

    def __init__(self, data):
        self.bits = BitReader(data)

    def _read_a_field(self):
        """Read A-field, return (addr_type, value)."""
        addr_type = self.bits.read_bits(2)
        value = self.bits.read_word()
        return (addr_type, value)

    def _read_b_field(self):
        """Read B-field, return symbol name."""
        length = self.bits.read_bits(3)
        if length == 0:
            length = 8
        name = ''
        for _ in range(length):
            name += chr(self.bits.read_byte())
        return name

    def read_item(self):
        """
        Read next item from REL file.
        Returns tuple describing the item, or None at end.
        """
        if self.bits.at_end():
            return None

        first_bit = self.bits.read_bit()

        if first_bit == 0:
            # Absolute byte
            return ('ABSOLUTE_BYTE', self.bits.read_byte())

        # Relocatable item
        reloc_type = self.bits.read_bits(2)

        if reloc_type == 0:
            # Special LINK item
            control = self.bits.read_bits(4)

            if control == LINK_ENTRY_SYMBOL:
                return ('ENTRY_SYMBOL', self._read_b_field())
            elif control == LINK_SELECT_COMMON:
                return ('SELECT_COMMON', self._read_b_field())
            elif control == LINK_PROGRAM_NAME:
                return ('PROGRAM_NAME', self._read_b_field())
            elif control == LINK_REQUEST_LIB:
                return ('REQUEST_LIB', self._read_b_field())
            elif control == LINK_DEFINE_COMMON_SIZE:
                a = self._read_a_field()
                b = self._read_b_field()
                return ('DEFINE_COMMON_SIZE', a, b)
            elif control == LINK_CHAIN_EXTERNAL:
                a = self._read_a_field()
                b = self._read_b_field()
                return ('CHAIN_EXTERNAL', a, b)
            elif control == LINK_DEFINE_ENTRY:
                a = self._read_a_field()
                b = self._read_b_field()
                return ('DEFINE_ENTRY', a, b)
            elif control == LINK_EXTERNAL_OFFSET:
                a = self._read_a_field()
                b = self._read_b_field()
                return ('EXTERNAL_OFFSET', a, b)
            elif control == LINK_EXTERNAL_PLUS_OFFSET:
                a = self._read_a_field()
                return ('EXTERNAL_PLUS_OFFSET', a)
            elif control == LINK_DEFINE_DATA_SIZE:
                a = self._read_a_field()
                return ('DEFINE_DATA_SIZE', a)
            elif control == LINK_SET_LOC:
                a = self._read_a_field()
                return ('SET_LOC', a)
            elif control == LINK_CHAIN_ADDRESS:
                a = self._read_a_field()
                return ('CHAIN_ADDRESS', a)
            elif control == LINK_DEFINE_PROG_SIZE:
                a = self._read_a_field()
                return ('DEFINE_PROG_SIZE', a)
            elif control == LINK_END_PROGRAM:
                self.bits.force_byte_boundary()
                return ('END_PROGRAM',)
            elif control == LINK_END_FILE:
                self.bits.force_byte_boundary()
                return ('END_FILE',)
            else:
                return ('UNKNOWN_SPECIAL', control)

        elif reloc_type == 1:
            # Program relative
            return ('PROGRAM_REL', self.bits.read_word())
        elif reloc_type == 2:
            # Data relative
            return ('DATA_REL', self.bits.read_word())
        elif reloc_type == 3:
            # Common relative
            return ('COMMON_REL', self.bits.read_word())

    def read_all(self):
        """Read all items, return as list."""
        items = []
        while True:
            item = self.read_item()
            if item is None:
                break
            items.append(item)
            if item[0] == 'END_FILE':
                break
        return items
