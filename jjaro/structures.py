import ctypes


MAX_FILENAME = 64
MAX_VERTEX_COUNT = 8
SIDE_COUNT = 6


class Metacls(type(ctypes.BigEndianStructure)):

    def __new__(metacls, name, bases, namespace):
        cls = super().__new__(metacls, name, bases, namespace)

        # Add a nice string representation for print().
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

    # TODO: How to override filename so it returns the correct non-roman string?
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


class Chunk(StructureBase):

    _fields_ = (
        ('tag',         ctypes.c_uint32),
        ('next_offset', ctypes.c_int32),
        ('size',        ctypes.c_int32),
        ('offset',      ctypes.c_int32),
    )


class Point(StructureBase):

    _fields_ = (
        ('x', ctypes.c_int16),
        ('y', ctypes.c_int16),
    )


class Line(StructureBase):

    _fields_ = [
        ('endpoint_indices',                    ctypes.c_int16 * 2),
        ('flags',                               ctypes.c_uint16),
        ('length',                              ctypes.c_int16),
        ('highest_adjacent_floor',              ctypes.c_int16),
        ('lowest_adjacent_ceiling',             ctypes.c_int16),
        ('clockwise_polygon_side_index',        ctypes.c_int16),
        ('counterclockwise_polygon_side_index', ctypes.c_int16),
        ('clockwise_polygon_owner',             ctypes.c_int16),
        ('counterclockwise_polygon_owner',      ctypes.c_int16),
        ('_padding',                            ctypes.c_uint8 * 12),
    ]


class Polygon(StructureBase):

    _fields_ = [
        ('type',                        ctypes.c_int16),
        ('flags',                       ctypes.c_uint16),
        ('permutation',                 ctypes.c_int16),
        ('vertex_count',                ctypes.c_uint16),
        ('endpoint_indices',            ctypes.c_int16 * MAX_VERTEX_COUNT),
        ('line_indices',                ctypes.c_int16 * MAX_VERTEX_COUNT),
        ('floor_texture',               ctypes.c_uint16),
        ('ceiling_texture',             ctypes.c_uint16),
        ('floor_height',                ctypes.c_int16),
        ('ceiling_height',              ctypes.c_int16),
        ('floor_light',                 ctypes.c_int16),
        ('ceiling_light',               ctypes.c_int16),
        ('_area',                       ctypes.c_int32),
        ('first_object_index',          ctypes.c_int16),
        ('_first_exclusion_zone_index', ctypes.c_int16),
        ('_line_exclusion_zone_count',  ctypes.c_int16),
        ('_point_exclusion_zone_count', ctypes.c_int16),
        ('floor_transfer_mode',         ctypes.c_int16),
        ('ceiling_transfer_mode',       ctypes.c_int16),
        ('adjacent_polygon_indices',    ctypes.c_int16 * MAX_VERTEX_COUNT),
        ('_first_neighbor_index',       ctypes.c_int16),
        ('_neighbor_count',             ctypes.c_int16),
        ('_center_x',                   ctypes.c_int16),
        ('_center_y',                   ctypes.c_int16),
        ('side_indices',                ctypes.c_int16 * SIDE_COUNT),

        # ('floor_origin_x', ctypes.c_int16),
        # ('floor_origin_y', ctypes.c_int16),
        # ('ceiling_origin_x', ctypes.c_int16),
        # ('ceiling_origin_y', ctypes.c_int16),

        ('floor_origin', Point),
        ('ceiling_origin', Point),


        ('media_index', ctypes.c_int16),
        ('media_light', ctypes.c_int16),
        ('_sound_source_indices', ctypes.c_int16),
        ('ambient_sound', ctypes.c_int16),
        ('random_sound', ctypes.c_int16),

        # TODO: Missing 8 bytes somewhere. Below should be 2 only.
        ('_padding', ctypes.c_uint8 * 6),               # 2 bytes skipped at the end
    ]


class CollectionHeader(StructureBase):

    _fields_ = (
        ('status',      ctypes.c_int16),
        ('flags',       ctypes.c_uint16),
        ('offset8',     ctypes.c_int32),
        ('length8',     ctypes.c_int32),
        ('offset16',    ctypes.c_int32),
        ('length16',    ctypes.c_int32),
        ('_unused',     ctypes.c_uint8 * 12),
    )


class Collection(StructureBase):

    _fields_ = (
        ('version',                         ctypes.c_int16),
        ('type',                            ctypes.c_int16),
        ('flags',                           ctypes.c_uint16),
        ('colors_per_table',                ctypes.c_int16),
        ('color_table_count',               ctypes.c_int16),
        ('color_tables_offset',             ctypes.c_int32),
        ('high_level_shape_count',          ctypes.c_int16),
        ('high_level_shape_table_offset',   ctypes.c_int32),
        ('low_level_shape_count',           ctypes.c_int16),
        ('low_level_shape_table_offset',    ctypes.c_int32),
        ('bitmap_count',                    ctypes.c_int16),
        ('bitmap_table_offset',             ctypes.c_int32),
        ('scale_factor',                    ctypes.c_int16),
        ('collection_size',                 ctypes.c_int32),
        ('_unused',                         ctypes.c_uint8 * 506),
    )


class ColorTable(StructureBase):

    _fields_ = (
        ('flags',   ctypes.c_uint8),
        ('value',   ctypes.c_uint8),
        ('red',     ctypes.c_uint16),
        ('green',   ctypes.c_uint16),
        ('blue',    ctypes.c_uint16),
    )


class BitmapHeader(StructureBase):

    _fields_ = [
        ('width',           ctypes.c_int16),
        ('height',          ctypes.c_int16),
        ('bytes_per_row',   ctypes.c_int16),
        ('flags',           ctypes.c_int16),
        ('bit_depth',       ctypes.c_int16),
        ('_unused',         ctypes.c_uint8 * 20),
    ]

    @property
    def column_major(self):
        return bool(self.flags & 1 << 7)
