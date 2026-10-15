import { execFile as execFileCallback, spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { promisify } from 'node:util';
import { join, resolve } from 'node:path';
import { networkInterfaces } from 'node:os';
import { pathToFileURL } from 'node:url';

const execFile = promisify(execFileCallback);
const DEFAULT_PORT = 8790;

export async function writeReviewPage(outDir) {
  const outputRoot = resolve(outDir);
  const stats = JSON.parse(await readFile(join(outputRoot, 'stats.json'), 'utf8'));
  const entries = Object.entries(stats)
    .filter(([name]) => name !== '_meta')
    .map(([name, record]) => ({ name, ...record }));
  const changes = entries.filter((entry) => entry.class === 'change').sort(compareEntries);
  const noise = entries.filter((entry) => entry.class === 'noise').sort(compareEntries);
  const unchanged = entries.filter((entry) => entry.class === 'unchanged').sort((a, b) => a.name.localeCompare(b.name));
  const html = renderPage({ changes, noise, unchanged });
  const pagePath = join(outputRoot, 'index.html');
  await mkdir(outputRoot, { recursive: true });
  await writeFile(pagePath, html);
  return pagePath;
}

export function renderPage({ changes, noise, unchanged }) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visual proof</title>
<style>
:root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f4f0f4; color: #312d36; }
* { box-sizing: border-box; }
body { margin: 0; background: #f4f0f4; }
main { width: min(1500px, calc(100% - 40px)); margin: 0 auto; padding: 40px 0 72px; }
header { display: flex; align-items: end; justify-content: space-between; gap: 24px; margin-bottom: 36px; }
h1 { margin: 0; font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: -0.04em; font-weight: 720; }
header p { max-width: 560px; margin: 10px 0 0; color: #746c78; line-height: 1.55; }
.summary { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }
.pill { border: 1px solid #d6cbd7; border-radius: 999px; padding: 8px 12px; background: #fffafd; color: #625968; font-size: 0.82rem; }
section { margin-top: 38px; }
h2 { display: flex; align-items: baseline; gap: 10px; margin: 0 0 14px; font-size: 1.35rem; letter-spacing: -0.02em; }
h2 span { color: #817787; font-size: 0.84rem; font-weight: 500; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 560px), 1fr)); gap: 18px; }
.card {
  overflow: hidden;
  border: 1px solid #ddd3df;
  border-radius: 16px;
  background: #fffafd;
  box-shadow: 0 8px 28px rgba(72, 55, 79, 0.08);
}
.card-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; padding: 14px 16px 12px; }
.story { min-width: 0; flex: 1 1 240px; font-weight: 680; overflow-wrap: anywhere; }
.meta { color: #756c7a; font-size: 0.83rem; }
.badge { border-radius: 999px; padding: 4px 9px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.badge-change { background: #f1d7e5; color: #8a3667; }
.badge-noise { background: #dceaf3; color: #41637a; }
.stats { display: flex; flex-wrap: wrap; gap: 6px 12px; width: 100%; color: #756c7a; font-size: 0.78rem; }
.triptych { display: block; width: 100%; height: auto; border-top: 1px solid #e4dbe5; background: #fff; }
.empty { border: 1px dashed #cfc2d1; border-radius: 14px; padding: 22px; color: #766c7a; background: rgba(255, 250, 253, 0.65); }
.unchanged { margin: 0; padding-left: 22px; color: #746a78; columns: 2 320px; column-gap: 42px; }
.unchanged li { margin: 5px 0; overflow-wrap: anywhere; }
@media (max-width: 760px) {
  main { width: min(100% - 24px, 1500px); padding-top: 24px; }
  header { display: block; }
  .summary { justify-content: flex-start; margin-top: 18px; }
}
</style>
</head>
<body>
<main>
<header>
<div>
  <h1>Visual proof</h1>
  <p>Review every changed capture at native scale. The diff locates movement; the owner decides whether it matches the intended target.</p>
</div>
<div class="summary">
  <span class="pill">${changes.length} changes</span>
  <span class="pill">${noise.length} noise</span>
  <span class="pill">${unchanged.length} unchanged</span>
</div>
</header>
${renderSection('Changes', changes, 'change')}
${renderSection('Noise', noise, 'noise')}
<section>
  <h2>Unchanged <span>${unchanged.length} capture${unchanged.length === 1 ? '' : 's'}</span></h2>
  ${unchanged.length
    ? `<ul class="unchanged">${unchanged.map((entry) => `<li>${escapeHtml(entry.name)}</li>`).join('')}</ul>`
    : '<div class="empty">No unchanged captures.</div>'}
</section>
</main>
</body>
</html>
`;
}

function renderSection(title, entries, kind) {
  const label = kind === 'change' ? 'above noise' : 'anti-aliasing and fringe candidates';
  const body = entries.length
    ? `<div class="grid">${entries.map((entry) => renderCard(entry, kind)).join('')}</div>`
    : '<div class="empty">No captures in this group.</div>';
  return `<section>
  <h2>${title} <span>${entries.length} capture${entries.length === 1 ? '' : 's'} · ${label}</span></h2>
  ${body}
</section>`;
}

function renderCard(entry, kind) {
  const { story, width } = parseCaptureName(entry.name);
  const mismatch = entry.sizeMismatch ? ' · padded size mismatch' : '';
  const share = entry.dominantPairShare ? ` · dominant pair ${Math.round(entry.dominantPairShare * 100)}%` : '';
  const stats = [
    `${entry.changedPixels} changed`,
    `${entry.softPixels} soft`,
    `${entry.strongPixels} strong`,
    `${entry.class}${mismatch}${share}`,
  ];
  return `<article class="card">
  <div class="card-meta">
    <span class="story">${escapeHtml(story)}</span>
    <span class="meta">${escapeHtml(width)}px</span>
    <span class="badge badge-${kind}">${kind}</span>
    <div class="stats">${stats.map((stat) => `<span>${escapeHtml(stat)}</span>`).join('')}</div>
  </div>
  <img class="triptych" src="${escapeAttribute(entry.triptych)}"
    alt="Before, after, and pixel diff for ${escapeAttribute(story)} at ${escapeAttribute(width)} pixels">
</article>`;
}

function parseCaptureName(name) {
  const match = name.match(/^(.*)@(\d+)\.png$/);
  return match ? { story: match[1], width: match[2] } : { story: name, width: 'unknown' };
}

function compareEntries(a, b) {
  return b.changedPixels - a.changedPixels || a.name.localeCompare(b.name);
}

function escapeHtml(value) {
  const entities = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(value).replace(/[&<>"']/g, (character) => entities[character]);
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, '&#96;');
}

function firstLanIpv4() {
  const interfaces = networkInterfaces();
  for (const addresses of Object.values(interfaces)) {
    for (const address of addresses ?? []) {
      if (address.family === 'IPv4' && !address.internal) return address.address;
    }
  }
  return '127.0.0.1';
}

async function servePage(outDir, port, host) {
  if (port === 8765) throw new Error('port 8765 is reserved and cannot be used');
  const outputRoot = resolve(outDir);
  const pageUrl = `http://${host}:${port}/index.html`;
  const server = spawn('python3', ['-m', 'http.server', String(port), '--bind', host], {
    cwd: outputRoot,
    stdio: 'inherit',
  });
  let settled = false;
  const exitPromise = new Promise((resolveExit, rejectExit) => {
    server.once('error', rejectExit);
    server.once('exit', (code, signal) => {
      if (!settled) rejectExit(new Error(`review server exited (${code ?? signal})`));
      else resolveExit();
    });
  });
  try {
    await waitForCurl(pageUrl);
    console.log(pageUrl);
    await exitPromise;
  } finally {
    settled = true;
    if (!server.killed) server.kill('SIGTERM');
  }
}

async function waitForCurl(url) {
  let lastError;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      await execFile('curl', ['--fail', '--silent', '--show-error', url], { maxBuffer: 1024 * 1024 });
      return;
    } catch (error) {
      lastError = error;
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 50));
    }
  }
  throw new Error(`could not curl ${url}: ${lastError?.message ?? 'server did not respond'}`);
}

function parseArgs(argv) {
  const values = { port: DEFAULT_PORT, host: firstLanIpv4(), serve: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help' || argument === '-h') return { help: true };
    if (argument === '--serve') { values.serve = true; continue; }
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
  values.port = Number(values.port);
  if (!Number.isInteger(values.port) || values.port < 1 || values.port > 65535) throw new Error('--port must be a valid TCP port');
  return values;
}

function usage() {
  return 'Usage: node scripts/page.mjs --out <dir> [--serve] [--port <port>] [--host <host>]';
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (args.help) {
      console.log(usage());
    } else {
      if (!args.out) throw new Error(usage());
      const pagePath = await writeReviewPage(args.out);
      console.log(`wrote ${pagePath}`);
      if (args.serve) await servePage(args.out, args.port, args.host);
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  }
}
