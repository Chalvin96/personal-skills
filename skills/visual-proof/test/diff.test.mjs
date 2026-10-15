import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { createRequire } from 'node:module';
import { diffDirectories } from '../scripts/diff.mjs';

const require = createRequire(import.meta.url);
const { PNG } = require('../vendor/pngjs');

test('identical pair writes stats without a triptych', async () => {
  const root = await mkdtemp(join(tmpdir(), 'visual-proof-test-'));
  try {
    const { before, after, out } = await fixtureDirectories(root);
    await writeFixture(join(before, 'same.png'), solid(4, 4, [255, 255, 255]));
    await writeFixture(join(after, 'same.png'), solid(4, 4, [255, 255, 255]));
    const stats = await diffDirectories({ beforeDir: before, afterDir: after, outDir: out });
    assert.equal(stats['same.png'].class, 'unchanged');
    assert.equal(stats['same.png'].changed, false);
    assert.deepEqual(await readdir(join(out, 'triptychs')), []);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('a one-pixel colour step over four is captured', async () => {
  const root = await mkdtemp(join(tmpdir(), 'visual-proof-test-'));
  try {
    const { before, after, out } = await fixtureDirectories(root);
    const beforeImage = solid(4, 4, [100, 100, 100]);
    const afterImage = solid(4, 4, [100, 100, 100]);
    setPixel(afterImage, 1, 1, [110, 100, 100]);
    await writeFixture(join(before, 'step.png'), beforeImage);
    await writeFixture(join(after, 'step.png'), afterImage);
    const stats = await diffDirectories({ beforeDir: before, afterDir: after, outDir: out });
    assert.equal(stats['step.png'].changedPixels, 1);
    assert.equal(stats['step.png'].softPixels, 1);
    assert.equal(stats['step.png'].class, 'change');
    assert.equal(stats['step.png'].triptych, 'triptychs/step.png');
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('scattered anti-aliasing fringes are noise', async () => {
  const root = await mkdtemp(join(tmpdir(), 'visual-proof-test-'));
  try {
    const { before, after, out } = await fixtureDirectories(root);
    const beforeImage = solid(8, 8, [100, 100, 100]);
    const afterImage = solid(8, 8, [100, 100, 100]);
    for (let index = 0; index < 8; index += 1) setPixel(afterImage, index, 0, [106 + index, 100, 100]);
    await writeFixture(join(before, 'fringe.png'), beforeImage);
    await writeFixture(join(after, 'fringe.png'), afterImage);
    const stats = await diffDirectories({ beforeDir: before, afterDir: after, outDir: out });
    assert.equal(stats['fringe.png'].changedPixels, 8);
    assert.equal(stats['fringe.png'].class, 'noise');
    assert.ok(stats['fringe.png'].dominantPairShare < 0.25);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test('a solid border change is a change', async () => {
  const root = await mkdtemp(join(tmpdir(), 'visual-proof-test-'));
  try {
    const { before, after, out } = await fixtureDirectories(root);
    const beforeImage = solid(10, 10, [255, 255, 255]);
    const afterImage = solid(10, 10, [255, 255, 255]);
    for (let x = 0; x < 10; x += 1) {
      setPixel(afterImage, x, 0, [0, 0, 0]);
      setPixel(afterImage, x, 9, [0, 0, 0]);
    }
    for (let y = 1; y < 9; y += 1) {
      setPixel(afterImage, 0, y, [0, 0, 0]);
      setPixel(afterImage, 9, y, [0, 0, 0]);
    }
    await writeFixture(join(before, 'border.png'), beforeImage);
    await writeFixture(join(after, 'border.png'), afterImage);
    const stats = await diffDirectories({ beforeDir: before, afterDir: after, outDir: out });
    assert.equal(stats['border.png'].class, 'change');
    assert.ok(stats['border.png'].dominantPairShare > 0.25);
    assert.deepEqual(stats['border.png'].bbox, { x: 0, y: 0, width: 10, height: 10 });
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

async function fixtureDirectories(root) {
  const before = join(root, 'before');
  const after = join(root, 'after');
  const out = join(root, 'out');
  await Promise.all([mkdir(before), mkdir(after), mkdir(out)]);
  return { before, after, out };
}

function solid(width, height, color) {
  const image = new PNG({ width, height });
  for (let index = 0; index < width * height; index += 1) {
    const offset = index * 4;
    image.data[offset] = color[0];
    image.data[offset + 1] = color[1];
    image.data[offset + 2] = color[2];
    image.data[offset + 3] = 255;
  }
  return image;
}

function setPixel(image, x, y, color) {
  const offset = (y * image.width + x) * 4;
  image.data[offset] = color[0];
  image.data[offset + 1] = color[1];
  image.data[offset + 2] = color[2];
  image.data[offset + 3] = 255;
}

async function writeFixture(path, image) {
  await writeFile(path, PNG.sync.write(image));
}
