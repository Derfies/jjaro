import struct

import numpy as np
from PIL import Image

from jjaro.structures import BitmapHeader, ColorTable, CollectionHeader, Collection


def scan_shapes(path):
    with open(path, 'rb') as f:

        headers = []
        for _ in range(32):
            header = CollectionHeader.from_stream(f)
            headers.append(header)

        for header in headers[0:1]:

            f.seek(header.offset8)
            collection = Collection.from_stream(f)

            palette = []
            f.seek(header.offset8 + collection.color_tables_offset)
            for _ in range(collection.color_table_count):
                for _ in range(collection.colors_per_table):
                    c = ColorTable.from_stream(f)
                    palette.append(c.rgb)

            palette = np.array(np.vstack(palette), dtype=np.uint8)

            offsets = []
            f.seek(header.offset8 + collection.bitmap_table_offset)
            for _ in range(collection.bitmap_count):
                offset = struct.unpack('>i', f.read(4))[0]
                offsets.append(offset)

            for offset in offsets[37:40]:
                f.seek(header.offset8 + offset)
                bitmap_header = BitmapHeader.from_stream(f)

                # Additional offset.
                bitmap_offset = 4 * bitmap_header.width if bitmap_header.column_major else 4 * bitmap_header.height
                f.seek(bitmap_offset, 1)

                raw = f.read(bitmap_header.width * bitmap_header.height)
                bitmap_indices = np.frombuffer(raw, dtype=np.uint8).reshape((bitmap_header.height, bitmap_header.width))

                #img = Image.fromarray(bitmap_indices, mode='L')
                #img.show()

                result = palette[bitmap_indices]
                img = Image.fromarray(result, 'RGB')
                img.show()



if __name__ == '__main__':
    import sys
    scan_shapes(sys.argv[1])
