import struct
import ctypes
from jjaro.structures import BitmapHeader, ColorTable, CollectionHeader, Collection

from PIL import Image
import numpy as np


COLLECTION_COUNT = 256  # number of possible collections (fixed table)
HEADER_SIZE = 128       # bytes at start of file before collection directory


def scan_shapes(path):
    with open(path, 'rb') as f:

        headers = []
        for _ in range(32):
            header = CollectionHeader.from_stream(f)
            headers.append(header)

        print('num collections:', len(headers))

        for header in headers[0:1]:

            f.seek(header.offset8)
            collection = Collection.from_stream(f)
            print(collection)

            f.seek(collection.color_tables_offset)
            for _ in range(collection.color_table_count):
                print('    ', ColorTable.from_stream(f))

            offsets = []
            f.seek(header.offset8 + collection.bitmap_table_offset)
            for _ in range(collection.bitmap_count):
                offset = struct.unpack('>i', f.read(4))[0]
                offsets.append(offset)

            for offset in offsets[37:38]:
                f.seek(header.offset8 + offset)
                bitmap_header = BitmapHeader.from_stream(f)

                # print('1:', 296 / bitmap_header.width)
                # print('2:', 296 / bitmap_header.height)

                bitmap_offset = 4 * bitmap_header.width if bitmap_header.column_major else 4 * bitmap_header.height

                #f.seek(f.tell() + 296)
                f.seek(bitmap_offset, 1)
                #print('    ', bitmap_header.column_major, bitmap_header)
                raw = f.read(bitmap_header.width * bitmap_header.height)
                img = Image.frombytes('L', (bitmap_header.width, bitmap_header.height), raw)
                img.show()

                arr_direct = np.frombuffer(raw, dtype=np.uint8).reshape((bitmap_header.height, bitmap_header.width))
                print(arr_direct)


if __name__ == '__main__':
    import sys
    scan_shapes(sys.argv[1])
