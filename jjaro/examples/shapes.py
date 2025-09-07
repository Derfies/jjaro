import struct

import numpy as np
from PIL import Image

from jjaro.structures import BitmapHeader, Color, CollectionHeader, Collection


def scan_shapes(path):
    with open(path, 'rb') as f:

        headers = []
        for _ in range(32):
            header = CollectionHeader.from_stream(f)
            headers.append(header)

        for header in headers[18:19]:

            f.seek(header.offset8)
            collection = Collection.from_stream(f)

            print(collection)

            colors = []
            f.seek(header.offset8 + collection.color_tables_offset)
            for _ in range(collection.color_table_count):
                for _ in range(collection.colors_per_table):
                    c = Color.from_stream(f)
                    colors.append(c.rgb)

            colors = np.array(np.vstack(colors), dtype=np.uint8)
            for i in range(0, 5):
                f.seek(header.offset8 + collection.bitmap_table_offset + i * 4)
                bitmap_header_offset = struct.unpack('>i', f.read(4))[0]

                f.seek(header.offset8 + bitmap_header_offset)
                bitmap_header = BitmapHeader.from_stream(f)

                # Additional offset.
                bitmap_offset = 4 * bitmap_header.width if bitmap_header.column_major else 4 * bitmap_header.height
                f.seek(bitmap_offset, 1)

                # Raw bitmap data.

                # uncompressed.
                if bitmap_header.bytes_per_row > -1:
                    raw = f.read(bitmap_header.width * bitmap_header.height)
                    bitmap_indices = np.frombuffer(raw, dtype=np.uint8).reshape((bitmap_header.height, bitmap_header.width))
                else:

                    # This should be correct for width, height since numpy is row-major
                    bitmap_indices = np.zeros((bitmap_header.height, bitmap_header.width), dtype=np.uint8)

                    # TODO: Switch based on row / column major.
                    # TODO: See if we can speed this up with more numpy magic.
                    # TODO: Fix transpose / rotation / flip whatever.

                    # READING COLUMNS.
                    for c in range(bitmap_header.width):
                        first_row, last_row = struct.unpack('>hh', f.read(4))
                        num_bytes = last_row - first_row
                        line = np.frombuffer(f.read(num_bytes), dtype=np.uint8)
                        bitmap_indices[first_row:last_row, c] = line

                try:
                    result = colors[bitmap_indices]
                    img = Image.fromarray(result, 'RGB')
                except:
                    print('FAILED')
                    img = Image.fromarray(bitmap_indices, 'L')
                img.show()


if __name__ == '__main__':
    import sys
    scan_shapes(sys.argv[1])
