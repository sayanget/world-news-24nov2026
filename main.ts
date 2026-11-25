// Entry for make.fun bounty news-image-20261124.
// The image is rendered at build time (see render/) and committed as entry.png;
// this program just copies it to the output directory.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1024 * 1024; // gate: a whole PNG/JPEG of at most 1 MiB
const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const bytes = readFileSync(join(here, "entry.png"));
const isPng = bytes.length > 8 && bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
const isJpeg = bytes.length > 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
if (!isPng && !isJpeg) throw new Error("entry.png is not a PNG or JPEG");
if (bytes.length > MAX_BYTES) throw new Error(`entry.png is ${bytes.length} bytes, over 1 MiB`);

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, "entry.png"), bytes);
process.stderr.write(`wrote ${join(outDir, "entry.png")} (${bytes.length} bytes, ${isPng ? "PNG" : "JPEG"})\n`);
