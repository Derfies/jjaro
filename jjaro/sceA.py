import ctypes
import io
from enum import Enum
from jjaro.structures import Chunk, Entry, Header, Line, Point, Polygon
from jjaro.util import pack_string


ChunkTag = Enum('ChunkTag', {
    item: pack_string(item)
    for item in [
        'LINS',
        'LITE',
        'Minf',
        'NOTE',
        'OBJS',
        'PNTS',
        'POLY',
        'SIDS',
        'ambi',
        'bonk',
        'medi',
        'plac',
        'plat',
    ]
})


class Scea:

    def __init__(self):
        self.header = None
        self.points = []
        self.lines = []
        self.polygons = []


def load_chunks(stream: io.BytesIO, cls, collection):
    while True:
        buf = stream.read(ctypes.sizeof(cls))
        if not buf:
            break
        chunk = cls.from_buffer_copy(buf)
        collection.append(chunk)


def load(file_path: str):
    m = Scea()

    with (open(file_path, 'rb') as f):
        #
        # fork_start = 0
        # if (MacBinaryHeader(reader.ReadBytes(128))) {
        # fork_start = 128;
        # }
        # reader.BaseStream.Seek(fork_start, SeekOrigin.Begin);

        #f.seek(128)

        # Header.
        m.header = Header.from_stream(f)
        f.read(40)  # Unused.
        f.seek(m.header.directory_offset)

        # Entries.
        entries = {}
        for i in range(m.header.wad_count):
            entry = Entry.from_stream(f)
            entries[entry.index] = entry
            f.read(m.header.directory_data_size)

        # TODO: Add fork start offset.
        # Each entry is a level, I suppose?
        #print(len(entries.values()))
        for entry in list(entries.values())[0:1]:
            f.seek(entry.offset)

            position = f.tell()
            while True:

                chunk = Chunk.from_stream(f)
                try:
                    tag = ChunkTag(chunk.tag)
                except:
                    pass

                else:
                    stream = io.BytesIO(f.read(chunk.size))

                    # Points
                    if tag == ChunkTag.PNTS:
                        load_chunks(stream, Point, m.points)
                    elif tag == ChunkTag.LINS:
                        load_chunks(stream, Line, m.lines)
                    elif tag == ChunkTag.POLY:
                        load_chunks(stream, Polygon, m.polygons)

                if chunk.next_offset > 0:
                    f.seek(position + chunk.next_offset)
                else:
                    break

    return m


if __name__ == '__main__':
    import sys
    file_path = sys.argv[1]
    m = load(file_path)

    print('points')
    for p in m.points:
        print(p)

    print('lines')
    for l in m.lines:
        print(l)

    print('polygons')
    for p in m.polygons[0:2]:

        print('\n\n')
        print(p)
        print('floor_origin:', p.floor_origin)
        print('ceiling_origin:', p.ceiling_origin)
        print('endpoint_indexes:')
        for i in range(len(p.endpoint_indices)):
            print('    ', i, '->', p.endpoint_indexes[i])

        print('line_indexes:')
        for i in range(len(p.line_indexes)):
            print('    ', i, '->', p.line_indexes[i])

        print('side_indexes:')
        for i in range(len(p.side_indexes)):
            print('    ', i, '->', p.side_indexes[i])
