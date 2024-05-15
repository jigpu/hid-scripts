#!/usr/bin/env python3

# Read and parse a binary HID descriptor into individual items.
#
# When called with a filename, prints the parsed items one per row
# both as hex and the type/tag/data.

import sys


def _parse_meta(meta):
    bSize = meta & 0x03
    bType = (meta >> 2) & 0x03
    bTag = (meta >> 4) & 0x0F
    return (bSize, bType, bTag)


def _is_long_item(meta):
    bSize, bType, bTag = _parse_meta(meta)
    return bSize == 2 and bType == 3 and bTag == 0x0F


def _read_with_eof(stream, n):
    ret = stream.read(n)
    if len(ret) != n:
        raise EOFError
    return ret


def _read_next_item_bytes(stream):
    buf = _read_with_eof(stream, 1)

    bSize, bType, Tag = _parse_meta(buf[0])
    read_size = bSize
    if read_size == 3:  # HID encodes len=4 with the value 3
        read_size = 4
    try:
        buf += _read_with_eof(stream, read_size)
    except EOFError as e:
        raise IndexError from e

    if _is_long_item(buf[0]):
        bDataSize = buf[1]
        bLongItemTag = buf[2]
        read_size = bDataSize
        try:
            buf += _read_with_eof(stream, read_size)
        except EOFError as e:
            raise IndexError from e

    return buf


def parse_item_bytes(buf):
    size, type, tag = _parse_meta(buf[0])
    data = buf[1:]
    if _is_long_item(buf[0]):
        size, tag = buf[1:3]
        data = buf[3:]
    return {"type": type, "tag": tag, "data": data}


def read_hid_binary_items(filename):
    items = []
    with open(filename, "rb") as f:
        try:
            while True:
                item = _read_next_item_bytes(f)
                items.append(item)
        except EOFError:
            pass
    return items


if __name__ == "__main__":
    items = read_hid_binary_items(sys.argv[1])
    for item in items:
        hex = " ".join(["{:02x}".format(x) for x in item])
        parse = parse_item_bytes(item)
        print(hex, parse)
