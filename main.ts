// news-image-20261122 entry (Node 22, standard library only).
// Validates the bundled entry.png — a newspaper-style summary of the
// world's news of Sunday, 22 November 2026 — then copies it to
// /output/entry.png. Outside the grader's container, MAKEFUN_OUTPUT_DIR
// stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const SRC = new URL('./entry.png', import.meta.url);
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576;
const MAX_DIM = 1024;

// The image must be a whole PNG: magic bytes, then the IHDR chunk
// carrying width and height, so the gate can read exactly the image
// the header describes.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const buf = readFileSync(SRC);
if (buf.length > MAX_BYTES) {
  throw new Error(`entry.png is ${buf.length} bytes, over the 1 MiB limit`);
}
if (!buf.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png does not start with the PNG magic bytes');
}
if (buf.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk where the PNG header belongs');
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width > MAX_DIM || height > MAX_DIM) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}

// Walk every chunk to the IEND marker, checking each chunk's CRC, so a
// truncated or corrupted file is refused instead of reaching the judge.
const crcTable = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();
const crc32 = (data) => {
  let c = 0xffffffff;
  for (const b of data) c = crcTable[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};
let offset = 8;
let sawIend = false;
while (offset + 12 <= buf.length) {
  const len = buf.readUInt32BE(offset);
  const type = buf.toString('ascii', offset + 4, offset + 8);
  if (offset + 12 + len > buf.length) {
    throw new Error(`entry.png chunk ${type} is truncated`);
  }
  const stored = buf.readUInt32BE(offset + 8 + len);
  const actual = crc32(buf.subarray(offset + 4, offset + 8 + len));
  if (stored !== actual) {
    throw new Error(`entry.png chunk ${type} fails its CRC check`);
  }
  offset += 12 + len;
  if (type === 'IEND') { sawIend = true; break; }
}
if (!sawIend) throw new Error('entry.png has no IEND chunk: the image is incomplete');
if (offset !== buf.length) throw new Error('entry.png has trailing bytes after IEND');

mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(SRC, join(OUT_DIR, 'entry.png'));
console.log(`entry.png: ${width}x${height}, ${buf.length} bytes -> ${join(OUT_DIR, 'entry.png')}`);
