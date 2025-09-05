import ctypes


MAX_FILENAME = 64


class Metacls(type(ctypes.BigEndianStructure)):

    def __new__(metacls, name, bases, namespace):
        cls = super().__new__(metacls, name, bases, namespace)

        def __str__(self):
            fields = getattr(cls, '_fields_')
            values = ', '.join(f'{f_name}={getattr(self, f_name)!r}' for f_name, _ in fields)
            return f'{name}({values})'
        cls.__str__ = __str__

        return cls


class StructureBase(ctypes.BigEndianStructure, metaclass=Metacls):

    _pack_ = 1

    @classmethod
    def from_stream(cls, stream):
        buf = stream.read(ctypes.sizeof(cls))
        if len(buf) < ctypes.sizeof(cls):
            raise EOFError('Not enough bytes to fill structure')
        return cls.from_buffer_copy(buf)


class Header(StructureBase):

    # TODO: How to override filename so it returns the correct string?
    _fields_ = (
        ('version',                     ctypes.c_int16),
        ('data_version',                ctypes.c_int16),
        ('filename',                    ctypes.c_char * MAX_FILENAME),
        ('checksum',                    ctypes.c_uint32),
        ('directory_offset',            ctypes.c_int32),
        ('wad_count',                   ctypes.c_int16),
        ('directory_data_size',         ctypes.c_int16),
        ('entry_header_size',           ctypes.c_uint16),
        ('directory_entry_base_size',   ctypes.c_uint16),
        ('parent_checksum',             ctypes.c_uint32),
    )


class Entry(StructureBase):

    _fields_ = (
        ('offset',  ctypes.c_int32),
        ('size',    ctypes.c_int32),
        ('index',   ctypes.c_int16),
    )


class Point(StructureBase):

    _fields_ = (
        ('x', ctypes.c_int16),
        ('y', ctypes.c_int16),
    )


class Line(StructureBase):

    _fields_ = [
        ('endpoint_indexes', ctypes.c_int16 * 2),
        ('flags', ctypes.c_uint16),
        ('length', ctypes.c_int16),
        ('highest_adjacent_floor', ctypes.c_int16),
        ('lowest_adjacent_ceiling', ctypes.c_int16),
        ('clockwise_polygon_side_index', ctypes.c_int16),
        ('counterclockwise_polygon_side_index', ctypes.c_int16),
        ('clockwise_polygon_owner', ctypes.c_int16),
        ('counterclockwise_polygon_owner', ctypes.c_int16),
        ('_padding', ctypes.c_uint8 * 12),
    ]
