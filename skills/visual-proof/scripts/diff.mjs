import { createRequire } from 'node:module';
import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import { basename, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { PNG } = require('../vendor/pngjs');

const SWEEP_THRESHOLD = 4;
const SOFT_THRESHOLD = 24;
const GUTTER = 16;
const SOFT_COLOR = [0, 170, 255];
const STRONG_COLOR = [255, 0, 170];

export async function diffDirectories({ beforeDir, afterDir, outDir }) {
  const beforeRoot = resolve(beforeDir);
  const afterRoot = resolve(afterDir);
  const outputRoot = resolve(outDir);
  const [beforeNames, afterNames] = await Promise.all([
    pngNames(beforeRoot),
    pngNames(afterRoot),
  ]);
  const names = [...new Set([...beforeNames, ...afterNames])].sort();
  if (names.length === 0) {
    throw new Error(`no PNG captures found in ${beforeRoot} or ${afterRoot}`);
  }
  for (const name of names) {
    if (!beforeNames.includes(name) || !afterNames.includes(name)) {
      throw new Error(`missing counterpart for ${name}`);
    }
  }

  const triptychRoot = join(outputRoot, 'triptychs');
  await rm(triptychRoot, { recursive: true, force: true });
  await mkdir(triptychRoot, { recursive: true });
  const stats = {
    _meta: {
      generatedAt: new Date().toISOString(),
      sweepThreshold: SWEEP_THRESHOLD,
      softThreshold: SOFT_THRESHOLD,
    },
  };

  for (const name of names) {
    const before = PNG.sync.read(await readFile(join(beforeRoot, name)));
    const after = PNG.sync.read(await readFile(join(afterRoot, name)));
    const result = analyzePair(before, after);
    const record = {
      beforeSize: { width: before.width, height: before.height },
      afterSize: { width: after.width, height: after.height },
      sizeMismatch: result.sizeMismatch,
      changed: result.changedPixels > 0,
      class: result.class,
      changedPixels: result.changedPixels,
      softPixels: result.softPixels,
      strongPixels: result.strongPixels,
      counts: {
        changed: result.changedPixels,
        soft: result.softPixels,
        strong: result.strongPixels,
      },
      bbox: result.bbox,
      dominantPair: result.dominantPair,
      dominantPairCount: result.dominantPairCount,
      dominantPairShare: result.dominantPairShare,
      triptych: null,
    };
    if (result.changedPixels > 0) {
      const triptychName = `${basename(name, '.png')}.png`;
      const triptychPath = join(triptychRoot, triptychName);
      await writeFile(triptychPath, PNG.sync.write(makeTriptych(before, after, result)));
      record.triptych = `triptychs/${triptychName}`;
    }
    stats[name] = record;
  }

  await mkdir(outputRoot, { recursive: true });
  await writeFile(join(outputRoot, 'stats.json'), `${JSON.stringify(stats, null, 2)}\n`);
  return stats;
}

export function analyzePair(before, after) {
  const width = Math.max(before.width, after.width);
  const height = Math.max(before.height, after.height);
  const paddedBefore = padImage(before, width, height);
  const paddedAfter = padImage(after, width, height);
  let changedPixels = 0;
  let softPixels = 0;
  let strongPixels = 0;
  let minX = width;
  let minY = height;
  let maxX = -1;
  let maxY = -1;
  const pairs = new Map();

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const delta = Math.max(
        Math.abs(paddedBefore.data[offset] - paddedAfter.data[offset]),
        Math.abs(paddedBefore.data[offset + 1] - paddedAfter.data[offset + 1]),
        Math.abs(paddedBefore.data[offset + 2] - paddedAfter.data[offset + 2]),
        Math.abs(paddedBefore.data[offset + 3] - paddedAfter.data[offset + 3]),
      );
      if (delta <= SWEEP_THRESHOLD) continue;
      changedPixels += 1;
      if (delta <= SOFT_THRESHOLD) softPixels += 1;
      else strongPixels += 1;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
      const beforeColor = colorAt(paddedBefore, offset);
      const afterColor = colorAt(paddedAfter, offset);
      const key = `${beforeColor.join(',')}→${afterColor.join(',')}`;
      const pair = pairs.get(key) ?? { before: beforeColor, after: afterColor, count: 0 };
      pair.count += 1;
      pairs.set(key, pair);
    }
  }

  if (changedPixels === 0) {
    return {
      width,
      height,
      sizeMismatch: before.width !== after.width || before.height !== after.height,
      changedPixels: 0,
      softPixels: 0,
      strongPixels: 0,
      class: 'unchanged',
      bbox: null,
      dominantPair: null,
      dominantPairCount: 0,
      dominantPairShare: 0,
      before: paddedBefore,
      after: paddedAfter,
    };
  }

  const dominantPair = [...pairs.values()].sort((a, b) => b.count - a.count)[0];
  const dominantPairShare = dominantPair.count / changedPixels;
  return {
    width,
    height,
    sizeMismatch: before.width !== after.width || before.height !== after.height,
    changedPixels,
    softPixels,
    strongPixels,
    class: dominantPairShare > 0.25 ? 'change' : 'noise',
    bbox: {
      x: minX,
      y: minY,
      width: maxX - minX + 1,
      height: maxY - minY + 1,
    },
    dominantPair: { before: dominantPair.before, after: dominantPair.after },
    dominantPairCount: dominantPair.count,
    dominantPairShare: Number(dominantPairShare.toFixed(6)),
    before: paddedBefore,
    after: paddedAfter,
  };
}

export function makeTriptych(before, after, result = analyzePair(before, after)) {
  const width = result.width;
  const height = result.height;
  const paddedBefore = result.before ?? padImage(before, width, height);
  const paddedAfter = result.after ?? padImage(after, width, height);
  const triptych = new PNG({ width: width * 3 + GUTTER * 2, height });
  fill(triptych, [255, 255, 255, 255]);
  copyPanel(paddedBefore, triptych, 0);
  copyPanel(paddedAfter, triptych, width + GUTTER);
  const diff = fadedPanel(paddedAfter, result);
  copyPanel(diff, triptych, width * 2 + GUTTER * 2);
  return triptych;
}

function fadedPanel(after, result) {
  const panel = new PNG({ width: result.width, height: result.height });
  for (let i = 0; i < result.width * result.height; i += 1) {
    const offset = i * 4;
    panel.data[offset] = Math.round(after.data[offset] * 0.2 + 255 * 0.8);
    panel.data[offset + 1] = Math.round(after.data[offset + 1] * 0.2 + 255 * 0.8);
    panel.data[offset + 2] = Math.round(after.data[offset + 2] * 0.2 + 255 * 0.8);
    panel.data[offset + 3] = 255;
    const delta = Math.max(
      Math.abs(result.before.data[offset] - after.data[offset]),
      Math.abs(result.before.data[offset + 1] - after.data[offset + 1]),
      Math.abs(result.before.data[offset + 2] - after.data[offset + 2]),
      Math.abs(result.before.data[offset + 3] - after.data[offset + 3]),
    );
    if (delta > SWEEP_THRESHOLD) {
      const color = delta <= SOFT_THRESHOLD ? SOFT_COLOR : STRONG_COLOR;
      panel.data[offset] = color[0];
      panel.data[offset + 1] = color[1];
      panel.data[offset + 2] = color[2];
    }
  }
  if (result.bbox) drawBox(panel, result.bbox);
  return panel;
}

function drawBox(panel, bbox) {
  const left = Math.max(0, bbox.x - 3);
  const top = Math.max(0, bbox.y - 3);
  const right = Math.min(panel.width - 1, bbox.x + bbox.width - 1 + 3);
  const bottom = Math.min(panel.height - 1, bbox.y + bbox.height - 1 + 3);
  for (let thickness = 0; thickness < 2; thickness += 1) {
    for (let x = left; x <= right; x += 1) {
      setColor(panel, x, Math.min(panel.height - 1, top + thickness), STRONG_COLOR);
      setColor(panel, x, Math.max(0, bottom - thickness), STRONG_COLOR);
    }
    for (let y = top; y <= bottom; y += 1) {
      setColor(panel, Math.min(panel.width - 1, left + thickness), y, STRONG_COLOR);
      setColor(panel, Math.max(0, right - thickness), y, STRONG_COLOR);
    }
  }
}

function setColor(png, x, y, color) {
  const offset = (y * png.width + x) * 4;
  png.data[offset] = color[0];
  png.data[offset + 1] = color[1];
  png.data[offset + 2] = color[2];
  png.data[offset + 3] = 255;
}

function copyPanel(source, target, xOffset) {
  for (let y = 0; y < source.height; y += 1) {
    const sourceOffset = y * source.width * 4;
    const targetOffset = (y * target.width + xOffset) * 4;
    source.data.copy(target.data, targetOffset, sourceOffset, sourceOffset + source.width * 4);
  }
}

function fill(png, color) {
  for (let i = 0; i < png.width * png.height; i += 1) {
    const offset = i * 4;
    png.data[offset] = color[0];
    png.data[offset + 1] = color[1];
    png.data[offset + 2] = color[2];
    png.data[offset + 3] = color[3];
  }
}

function padImage(source, width, height) {
  const padded = new PNG({ width, height });
  fill(padded, [255, 255, 255, 255]);
  for (let y = 0; y < source.height; y += 1) {
    const sourceOffset = y * source.width * 4;
    const targetOffset = y * width * 4;
    source.data.copy(padded.data, targetOffset, sourceOffset, sourceOffset + source.width * 4);
  }
  return padded;
}

function colorAt(png, offset) {
  return [png.data[offset], png.data[offset + 1], png.data[offset + 2]];
}

async function pngNames(directory) {
  return (await readdir(directory)).filter((name) => name.endsWith('.png')).sort();
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help' || argument === '-h') return { help: true };
    if (!argument.startsWith('--')) throw new Error(`unknown argument: ${argument}`);
    const [key, inlineValue] = argument.slice(2).split('=', 2);
    if (inlineValue !== undefined) values[key] = inlineValue;
    else {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error(`missing value for --${key}`);
      values[key] = value;
      index += 1;
    }
  }
  return values;
}

function usage() {
  return 'Usage: node scripts/diff.mjs --before <dir> --after <dir> --out <dir>';
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (args.help) {
      console.log(usage());
    } else {
      if (!args.before || !args.after || !args.out) throw new Error(usage());
      const stats = await diffDirectories({
        beforeDir: args.before,
        afterDir: args.after,
        outDir: args.out,
      });
      const changed = Object.values(stats).filter((record) => record && record.changed).length;
      console.log(`wrote ${resolve(args.out, 'stats.json')} (${changed} changed)`);
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  }
}
