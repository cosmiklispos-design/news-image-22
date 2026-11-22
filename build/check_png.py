#!/usr/bin/env python3
"""Local gate check for the news-image-20261122 entry: PNG magic, size,
dimensions, per-chunk CRCs, IEND, no trailing bytes. Mirrors main.ts.
Run:  python3 build/check_png.py
"""
import struct
import sys
import zlib

PATH = "entry.png"

data = open(PATH, "rb").read()
assert len(data) <= 1048576, f"{len(data)} bytes, over the 1 MiB limit"
assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG magic"
assert data[12:16] == b"IHDR", "no IHDR chunk"
w, h = struct.unpack(">II", data[16:24])
assert w <= 1024 and h <= 1024, f"{w}x{h}, over the 1024x1024 limit"
off, saw_iend = 8, False
while off + 12 <= len(data):
    ln, typ = struct.unpack(">I", data[off:off + 4])[0], data[off + 4:off + 8]
    assert off + 12 + ln <= len(data), f"chunk {typ} truncated"
    stored = struct.unpack(">I", data[off + 8 + ln:off + 12 + ln])[0]
    actual = zlib.crc32(data[off + 4:off + 8 + ln]) & 0xFFFFFFFF
    assert stored == actual, f"chunk {typ} fails its CRC check"
    off += 12 + ln
    if typ == b"IEND":
        saw_iend = True
        break
assert saw_iend, "no IEND chunk"
assert off == len(data), "trailing bytes after IEND"
print(f"OK: {PATH} is {w}x{h}, {len(data)} bytes, all chunks valid")
sys.exit(0)
