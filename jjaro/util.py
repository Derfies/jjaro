def unpack_string(value: int) -> str:
    """
    Unpack a 32-bit int back into a 4-character string.

    """
    return ''.join([
        chr((value >> 24) & 0xFF),
        chr((value >> 16) & 0xFF),
        chr((value >> 8)  & 0xFF),
        chr(value & 0xFF)
    ])


def pack_string(s: str) -> int:
    """
    Pack a 4-character string into a 32-bit int.

    """
    if len(s) != 4:
        raise ValueError('Input must be exactly 4 characters')
    return (
        (ord(s[0]) << 24) |
        (ord(s[1]) << 16) |
        (ord(s[2]) << 8)  |
        ord(s[3])
    )
