/**
 * Generate LearnFlow mini program tab bar icon placeholders.
 * Creates 81x81 pixel PNG files with simple shapes using only Node.js built-ins.
 *
 * Usage: node generate-icons.js
 * Output: ../src/static/tabs/{home,learn,add,profile}.png and *-active.png
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const WIDTH = 81;
const HEIGHT = 81;
const OUT_DIR = path.resolve(__dirname, '..', 'src', 'static', 'tabs');

// Colors
const GRAY = { r: 0x99, g: 0x99, b: 0x99 };
const BLUE = { r: 0x40, g: 0x9e, b: 0xff };
const TRANSPARENT = { r: 0, g: 0, b: 0, a: 0 };

// ---------------------------------------------------------------------------
// PNG encoder (minimal, using built-in zlib)
// ---------------------------------------------------------------------------

function crc32(buf) {
  let c, crcTable = [];
  for (let n = 0; n < 256; n++) {
    c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    crcTable[n] = c >>> 0;
  }
  let crc = 0xffffffff;
  for (let i = 0; i < buf.length; i++) crc = crcTable[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function makeChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeAndData = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(typeAndData), 0);
  return Buffer.concat([len, typeAndData, crc]);
}

function encodePNG(pixels) {
  // pixels: Uint8Array of HEIGHT rows, each row: filterByte(0) + WIDTH * 4 (RGBA)
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  // IHDR
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(WIDTH, 0);
  ihdr.writeUInt32BE(HEIGHT, 4);
  ihdr[8] = 8;  // bit depth
  ihdr[9] = 6;  // color type: RGBA
  ihdr[10] = 0; // compression
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // interlace

  // Raw image data: each row = filter byte (0) + RGBA pixels
  const raw = Buffer.alloc(HEIGHT * (1 + WIDTH * 4));
  for (let y = 0; y < HEIGHT; y++) {
    const rowOffset = y * (1 + WIDTH * 4);
    raw[rowOffset] = 0; // filter: None
    for (let x = 0; x < WIDTH; x++) {
      const srcIdx = (y * WIDTH + x) * 4;
      const dstIdx = rowOffset + 1 + x * 4;
      raw[dstIdx]     = pixels[srcIdx];     // R
      raw[dstIdx + 1] = pixels[srcIdx + 1]; // G
      raw[dstIdx + 2] = pixels[srcIdx + 2]; // B
      raw[dstIdx + 3] = pixels[srcIdx + 3]; // A
    }
  }

  const compressed = zlib.deflateSync(raw);

  const iend = Buffer.alloc(0);

  return Buffer.concat([
    signature,
    makeChunk('IHDR', ihdr),
    makeChunk('IDAT', compressed),
    makeChunk('IEND', iend),
  ]);
}

// ---------------------------------------------------------------------------
// Drawing helpers
// ---------------------------------------------------------------------------

function createCanvas() {
  return Buffer.alloc(WIDTH * HEIGHT * 4, 0); // RGBA, all transparent
}

function setPixel(canvas, x, y, color, alpha = 255) {
  if (x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT) return;
  const idx = (y * WIDTH + x) * 4;
  // Alpha blend
  const a = alpha / 255;
  const existA = canvas[idx + 3] / 255;
  const outA = a + existA * (1 - a);
  if (outA === 0) return;
  canvas[idx]     = Math.round((color.r * a + canvas[idx]     * existA * (1 - a)) / outA);
  canvas[idx + 1] = Math.round((color.g * a + canvas[idx + 1] * existA * (1 - a)) / outA);
  canvas[idx + 2] = Math.round((color.b * a + canvas[idx + 2] * existA * (1 - a)) / outA);
  canvas[idx + 3] = Math.round(outA * 255);
}

function fillRect(canvas, x0, y0, w, h, color, alpha = 255) {
  for (let y = y0; y < y0 + h; y++)
    for (let x = x0; x < x0 + w; x++)
      setPixel(canvas, x, y, color, alpha);
}

function fillCircle(canvas, cx, cy, r, color, alpha = 255) {
  for (let y = cy - r; y <= cy + r; y++)
    for (let x = cx - r; x <= cx + r; x++)
      if ((x - cx) ** 2 + (y - cy) ** 2 <= r * r)
        setPixel(canvas, Math.round(x), Math.round(y), color, alpha);
}

function fillTriangle(canvas, x1, y1, x2, y2, x3, y3, color, alpha = 255) {
  const minY = Math.max(0, Math.min(y1, y2, y3));
  const maxY = Math.min(HEIGHT - 1, Math.max(y1, y2, y3));
  for (let y = minY; y <= maxY; y++) {
    for (let x = 0; x < WIDTH; x++) {
      if (pointInTriangle(x, y, x1, y1, x2, y2, x3, y3)) {
        setPixel(canvas, x, y, color, alpha);
      }
    }
  }
}

function pointInTriangle(px, py, x1, y1, x2, y2, x3, y3) {
  const d1 = sign(px, py, x1, y1, x2, y2);
  const d2 = sign(px, py, x2, y2, x3, y3);
  const d3 = sign(px, py, x3, y3, x1, y1);
  const hasNeg = (d1 < 0) || (d2 < 0) || (d3 < 0);
  const hasPos = (d1 > 0) || (d2 > 0) || (d3 > 0);
  return !(hasNeg && hasPos);
}

function sign(px, py, x1, y1, x2, y2) {
  return (px - x2) * (y1 - y2) - (x1 - x2) * (py - y2);
}

// Draw a thick line (rectangle from (x1,y1) to (x2,y2) with given thickness)
function drawThickLine(canvas, x1, y1, x2, y2, thickness, color, alpha = 255) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len === 0) return;
  const nx = -dy / len * thickness / 2;
  const ny = dx / len * thickness / 2;

  const minX = Math.max(0, Math.floor(Math.min(x1 + nx, x1 - nx, x2 + nx, x2 - nx)));
  const maxX = Math.min(WIDTH - 1, Math.ceil(Math.max(x1 + nx, x1 - nx, x2 + nx, x2 - nx)));
  const minY = Math.max(0, Math.floor(Math.min(y1 + ny, y1 - ny, y2 + ny, y2 - ny)));
  const maxY = Math.min(HEIGHT - 1, Math.ceil(Math.max(y1 + ny, y1 - ny, y2 + ny, y2 - ny)));

  for (let y = minY; y <= maxY; y++) {
    for (let x = minX; x <= maxX; x++) {
      // Distance from point to line segment
      const t = Math.max(0, Math.min(1, ((x - x1) * dx + (y - y1) * dy) / (len * len)));
      const projX = x1 + t * dx;
      const projY = y1 + t * dy;
      const dist = Math.sqrt((x - projX) ** 2 + (y - projY) ** 2);
      if (dist <= thickness / 2) {
        setPixel(canvas, x, y, color, alpha);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Icon drawing functions
// ---------------------------------------------------------------------------

function drawHome(canvas, color) {
  const cx = 40;
  // Roof: triangle
  fillTriangle(canvas, cx, 12, 12, 38, 68, 38, color);
  // Body: rectangle
  fillRect(canvas, 20, 38, 41, 28, color);
  // Door: cut out a small rectangle at bottom center
  fillRect(canvas, 34, 48, 13, 18, { r: 0, g: 0, b: 0 }, 0); // transparent door
  // Redraw door outline
  fillRect(canvas, 34, 48, 13, 18, color, 60);
  // Chimney
  fillRect(canvas, 52, 16, 7, 16, color);
}

function drawBook(canvas, color) {
  // Book body (left page)
  fillRect(canvas, 14, 16, 26, 48, color);
  // Book body (right page)
  fillRect(canvas, 42, 16, 26, 48, color);
  // Spine (center gap with slight overlap)
  fillRect(canvas, 38, 14, 5, 52, color);
  // Page lines on left
  for (let i = 0; i < 3; i++) {
    fillRect(canvas, 19, 26 + i * 12, 16, 2, { r: 255, g: 255, b: 255 }, 180);
  }
  // Page lines on right
  for (let i = 0; i < 3; i++) {
    fillRect(canvas, 47, 26 + i * 12, 16, 2, { r: 255, g: 255, b: 255 }, 180);
  }
}

function drawPlus(canvas, color) {
  const cx = 40, cy = 40;
  const armLen = 24;
  const thickness = 10;
  // Horizontal bar
  fillRect(canvas, cx - armLen, cy - thickness / 2, armLen * 2, thickness, color);
  // Vertical bar
  fillRect(canvas, cx - thickness / 2, cy - armLen, thickness, armLen * 2, color);
  // Circle border around plus
  for (let y = 0; y < HEIGHT; y++) {
    for (let x = 0; x < WIDTH; x++) {
      const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
      if (dist >= 28 && dist <= 32) {
        setPixel(canvas, x, y, color);
      }
    }
  }
}

function drawProfile(canvas, color) {
  const cx = 40;
  // Head: circle
  fillCircle(canvas, cx, 24, 13, color);
  // Body: ellipse / trapezoid shape (simplified as a wide arc)
  for (let y = 44; y < 70; y++) {
    const progress = (y - 44) / 26;
    const halfW = 12 + progress * 16;
    for (let x = Math.round(cx - halfW); x <= Math.round(cx + halfW); x++) {
      setPixel(canvas, x, y, color);
    }
  }
}

// ---------------------------------------------------------------------------
// Main: generate all 8 icons
// ---------------------------------------------------------------------------

const icons = [
  { name: 'home',    draw: drawHome },
  { name: 'learn',   draw: drawBook },
  { name: 'add',     draw: drawPlus },
  { name: 'profile', draw: drawProfile },
];

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

for (const icon of icons) {
  for (const active of [false, true]) {
    const canvas = createCanvas();
    const color = active ? BLUE : GRAY;
    icon.draw(canvas, color);

    const pngData = encodePNG(canvas);
    const suffix = active ? '-active' : '';
    const filePath = path.join(OUT_DIR, `${icon.name}${suffix}.png`);
    fs.writeFileSync(filePath, pngData);
    console.log(`Generated: ${filePath} (${pngData.length} bytes)`);
  }
}

console.log('\nAll 8 tab bar icons generated successfully!');
