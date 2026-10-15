import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { createServer } from 'node:http';
import { mkdir, mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { extname, join, resolve } from 'node:path';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const DEFAULT_WIDTHS = [320, 768, 1024, 1440];
const DEFAULT_BUILD_COMMAND = 'pnpm build-storybook';
const DEFAULT_APP_DIR = 'frontend';
const BUILD_TIMEOUT = 20 * 60 * 1000;
const CAPTURE_TIMEOUT = 45 * 1000;

export async function capture(options) {
  const projectRoot = await git(['rev-parse', '--show-toplevel'], options.cwd ?? process.cwd());
  const outRoot = resolve(options.out);
  const appDir = options.appDir ?? DEFAULT_APP_DIR;
  const widths = options.widths ?? DEFAULT_WIDTHS;
  const storiesOption = options.stories ?? 'all';
  const buildCommand = options.buildCmd ?? DEFAULT_BUILD_COMMAND;
  const buildEnv = { ...process.env, ...(options.env ?? {}) };
  const temporaryRoot = await mkdtemp(join(tmpdir(), 'visual-proof-'));
  const worktrees = [];
  const servers = [];
  let browser;

  await rm(join(outRoot, 'before'), { recursive: true, force: true });
  await rm(join(outRoot, 'after'), { recursive: true, force: true });
  await rm(join(outRoot, 'triptychs'), { recursive: true, force: true });
  await rm(join(outRoot, 'stats.json'), { force: true });
  await rm(join(outRoot, 'index.html'), { force: true });
  await rm(join(outRoot, 'capture.json'), { force: true });
  await mkdir(join(outRoot, 'before'), { recursive: true });
  await mkdir(join(outRoot, 'after'), { recursive: true });

  try {
    const baseRef = options.base ?? await defaultBaseRef(projectRoot);
    const baseRoot = await addWorktree(projectRoot, baseRef, join(temporaryRoot, 'base'));
    worktrees.push(baseRoot);
    await installDependencies(baseRoot, appDir);

    let headRoot = projectRoot;
    if (options.head && options.head !== 'worktree') {
      headRoot = await addWorktree(projectRoot, options.head, join(temporaryRoot, 'head'));
      worktrees.push(headRoot);
      await installDependencies(headRoot, appDir);
    } else {
      await installDependencies(headRoot, appDir, { skipWhenPresent: true });
    }

    const baseBuild = join(temporaryRoot, 'base-build');
    const headBuild = join(temporaryRoot, 'head-build');
    await buildStorybook(baseRoot, appDir, buildCommand, buildEnv, baseBuild);
    await buildStorybook(headRoot, appDir, buildCommand, buildEnv, headBuild);
    await assertBuildDirectory(baseBuild);
    await assertBuildDirectory(headBuild);

    const baseServer = await serveDirectory(baseBuild);
    const headServer = await serveDirectory(headBuild);
    servers.push(baseServer, headServer);
    await Promise.all([
      assertServedBuild(baseServer, baseBuild),
      assertServedBuild(headServer, headBuild),
    ]);

    const [baseIndex, headIndex] = await Promise.all([
      fetchStoryIndex(baseServer),
      fetchStoryIndex(headServer),
    ]);
    const stories = selectStories(storiesOption, headIndex, baseIndex);
    browser = await chromium.launch({ headless: true });
    await captureBuild(browser, baseServer.url, stories, widths, join(outRoot, 'before'));
    await captureBuild(browser, headServer.url, stories, widths, join(outRoot, 'after'));
    await writeFile(join(outRoot, 'capture.json'), `${JSON.stringify({
      base: baseRef,
      head: options.head ?? 'worktree',
      stories: stories.map((story) => story.id),
      widths,
      appDir,
      buildCommand,
      env: options.env ?? {},
    }, null, 2)}\n`);
    return { outRoot, stories, widths };
  } finally {
    if (browser) await browser.close().catch(() => {});
    for (const server of servers.reverse()) await server.close().catch(() => {});
    for (const worktree of worktrees.reverse()) {
      await git(['worktree', 'remove', '--force', worktree], projectRoot).catch(() => {});
    }
    await rm(temporaryRoot, { recursive: true, force: true });
  }
}

export function selectStories(selection, headIndex, baseIndex) {
  const headStories = storyEntries(headIndex);
  const baseStories = storyEntries(baseIndex);
  const baseIds = new Set(baseStories.map((story) => story.id));
  const headById = new Map(headStories.map((story) => [story.id, story]));
  const requested = selection === 'all'
    ? headStories.map((story) => story.id)
    : String(selection).split(',').map((id) => id.trim()).filter(Boolean);
  if (requested.length === 0) throw new Error('no stories were requested');
  const missingHead = requested.filter((id) => !headById.has(id));
  if (missingHead.length) throw new Error(`stories missing from head index.json: ${missingHead.join(', ')}`);
  const missingBase = requested.filter((id) => !baseIds.has(id));
  if (missingBase.length) throw new Error(`stories missing from base index.json: ${missingBase.join(', ')}`);
  return requested.map((id) => headById.get(id));
}

export function storyEntries(index) {
  const source = index?.entries ?? index?.stories ?? {};
  const records = Array.isArray(source)
    ? source.map((entry) => [entry.id, entry])
    : Object.entries(source);
  return records
    .map(([id, entry]) => ({ id: entry.id ?? id, ...entry }))
    .filter((entry) => entry.type === undefined || entry.type === 'story')
    .sort((a, b) => a.id.localeCompare(b.id));
}

async function captureBuild(browser, baseUrl, stories, widths, outputDir) {
  await mkdir(outputDir, { recursive: true });
  for (const width of widths) {
    const context = await browser.newContext({
      viewport: { width, height: 900 },
      deviceScaleFactor: 1,
      reducedMotion: 'reduce',
    });
    await context.addInitScript(() => {
      const disableMotion = () => {
        const style = document.createElement('style');
        style.textContent = [
          '*,:before,:after{',
          'animation-duration:0s!important;',
          'animation-delay:0s!important;',
          'transition-duration:0s!important;',
          'transition-delay:0s!important;',
          'scroll-behavior:auto!important}',
        ].join('');
        document.documentElement.appendChild(style);
      };
      if (document.documentElement) disableMotion();
      else document.addEventListener('DOMContentLoaded', disableMotion, { once: true });
    });
    try {
      for (const story of stories) {
        const page = await context.newPage();
        const failures = [];
        page.on('pageerror', (error) => failures.push(`pageerror: ${error.message}`));
        page.on('requestfailed', (request) => failures.push(
          `requestfailed: ${request.url()} (${request.failure()?.errorText ?? 'unknown'})`,
        ));
        page.on('console', (message) => {
          if (message.type() === 'error') failures.push(`console: ${message.text()}`);
        });
        const url = `${baseUrl}/iframe.html?id=${encodeURIComponent(story.id)}&viewMode=story`;
        try {
          await page.goto(url, { waitUntil: 'networkidle', timeout: CAPTURE_TIMEOUT });
          await page.waitForSelector('#storybook-root, #root', { state: 'attached', timeout: CAPTURE_TIMEOUT });
          await page.evaluate(async () => {
            if (document.fonts?.ready) await document.fonts.ready;
          });
          await page.waitForLoadState('networkidle', { timeout: CAPTURE_TIMEOUT });
          const storyError = await page.evaluate(() => {
            const element = document.querySelector('.sb-errordisplay,[data-testid="storybook-error"]');
            if (!element) return '';
            const style = getComputedStyle(element);
            const bounds = element.getBoundingClientRect();
            return style.display === 'none' || bounds.width === 0 || bounds.height === 0 ? '' : element.textContent?.trim() ?? '';
          });
          if (storyError) failures.push(`storybook error: ${storyError}`);
          if (failures.length) throw new Error(failures.join('\n'));
          const path = join(outputDir, `${safeStoryId(story.id)}@${width}.png`);
          await page.screenshot({ path, fullPage: true, animations: 'disabled' });
          const image = await stat(path);
          if (image.size === 0) throw new Error(`empty screenshot: ${path}`);
        } catch (error) {
          throw new Error(`capture failed for ${story.id} at ${width}px: ${error instanceof Error ? error.message : error}`);
        } finally {
          await page.close().catch(() => {});
        }
      }
    } finally {
      await context.close();
    }
  }
}

function safeStoryId(id) {
  return id.replace(/[^a-zA-Z0-9._-]/g, '_');
}

async function buildStorybook(treeRoot, appDir, buildCommand, env, outputDir) {
  const buildCwd = resolve(treeRoot, appDir);
  await mkdir(outputDir, { recursive: true });
  const command = /(?:^|\s)(?:--output-dir|-o)(?:\s|=)/.test(buildCommand)
    ? buildCommand
    : `${buildCommand} --output-dir ${shellQuote(outputDir)}`;
  await runProcess('sh', ['-lc', command], {
    cwd: buildCwd,
    env,
    stdio: 'inherit',
    timeout: BUILD_TIMEOUT,
  });
}

async function assertBuildDirectory(directory) {
  const indexPath = join(directory, 'index.html');
  const index = await stat(indexPath).catch(() => null);
  if (!index?.isFile()) throw new Error(`Storybook build did not produce ${indexPath}`);
  const storyIndex = await stat(join(directory, 'index.json')).catch(() => null);
  if (!storyIndex?.isFile()) throw new Error(`Storybook build did not produce ${join(directory, 'index.json')}`);
}

async function fetchStoryIndex(server) {
  const response = await fetch(`${server.url}/index.json`);
  if (!response.ok) throw new Error(`could not read ${server.url}/index.json (${response.status})`);
  return response.json();
}

async function assertServedBuild(server, buildDirectory) {
  const localPath = join(buildDirectory, 'index.html');
  const localBytes = await readFile(localPath);
  const response = await fetch(`${server.url}/index.html`);
  if (!response.ok) throw new Error(`served build returned ${response.status} for ${server.url}/index.html`);
  const servedBytes = Buffer.from(await response.arrayBuffer());
  const localHash = createHash('sha256').update(localBytes).digest('hex');
  const servedHash = createHash('sha256').update(servedBytes).digest('hex');
  if (localHash !== servedHash) throw new Error(`served build hash mismatch at ${server.url}: expected ${localHash}, got ${servedHash}`);
}

async function serveDirectory(root) {
  const server = createServer((request, response) => {
    serveRequest(root, request, response).catch((error) => {
      response.statusCode = error.code === 'ENOENT' ? 404 : 500;
      response.end(error.code === 'ENOENT' ? 'Not found' : error.message);
    });
  });
  await new Promise((resolveListen, rejectListen) => {
    server.once('error', rejectListen);
    server.listen(0, '127.0.0.1', resolveListen);
  });
  const address = server.address();
  const port = typeof address === 'object' && address ? address.port : null;
  if (!port) throw new Error('could not determine Storybook server port');
  return {
    url: `http://127.0.0.1:${port}`,
    close: () => new Promise((resolveClose) => server.close(() => resolveClose())),
  };
}

async function serveRequest(root, request, response) {
  const requestUrl = new URL(request.url ?? '/', 'http://127.0.0.1');
  const decodedPath = decodeURIComponent(requestUrl.pathname);
  const candidate = resolve(root, `.${decodedPath}`);
  if (candidate !== root && !candidate.startsWith(`${root}/`)) {
    response.statusCode = 403;
    response.end('Forbidden');
    return;
  }
  let path = candidate;
  const details = await stat(path);
  if (details.isDirectory()) path = join(path, 'index.html');
  response.statusCode = 200;
  response.setHeader('Content-Type', contentType(extname(path)));
  createReadStream(path).pipe(response);
}

function contentType(extension) {
  return ({
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
  })[extension] ?? 'application/octet-stream';
}

async function installDependencies(treeRoot, appDir, { skipWhenPresent = false } = {}) {
  const packageInfo = await packageManager(treeRoot, appDir);
  if (skipWhenPresent && await stat(join(packageInfo.cwd, 'node_modules')).catch(() => null)) return;
  await runProcess(packageInfo.command, packageInfo.args, { cwd: packageInfo.cwd, stdio: 'inherit' });
}

async function packageManager(treeRoot, appDir) {
  const candidates = [resolve(treeRoot), resolve(treeRoot, appDir)];
  for (const cwd of candidates) {
    const lock = await findLock(cwd);
    if (lock) return { ...lock, cwd };
  }
  return { command: 'npm', args: ['install'], cwd: resolve(treeRoot) };
}

async function findLock(directory) {
  const names = await readdir(directory).catch(() => []);
  if (names.includes('pnpm-lock.yaml')) return { command: 'pnpm', args: ['install', '--frozen-lockfile'] };
  if (names.includes('yarn.lock')) return { command: 'yarn', args: ['install', '--immutable'] };
  if (names.includes('package-lock.json')) return { command: 'npm', args: ['ci'] };
  if (names.includes('bun.lockb') || names.includes('bun.lock')) return { command: 'bun', args: ['install', '--frozen-lockfile'] };
  return null;
}

async function addWorktree(projectRoot, ref, path) {
  await mkdir(resolve(path, '..'), { recursive: true });
  await runProcess('git', ['worktree', 'add', '--detach', path, ref], { cwd: projectRoot, stdio: 'inherit' });
  return path;
}

async function defaultBaseRef(projectRoot) {
  const originHead = await git(['symbolic-ref', '--quiet', 'refs/remotes/origin/HEAD'], projectRoot).catch(() => null);
  if (originHead) return git(['merge-base', originHead, 'HEAD'], projectRoot);
  for (const candidate of ['origin/master', 'origin/main']) {
    const exists = await git(['rev-parse', '--verify', candidate], projectRoot).catch(() => null);
    if (exists) return git(['merge-base', candidate, 'HEAD'], projectRoot);
  }
  throw new Error('could not resolve the default base; pass --base <ref>');
}

async function git(args, cwd) {
  const result = await runProcess('git', args, { cwd });
  return result.stdout.trim();
}

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`;
}

function runProcess(command, args, options = {}) {
  return new Promise((resolveProcess, rejectProcess) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      env: options.env,
      stdio: options.stdio ?? 'pipe',
    });
    let stdout = '';
    let stderr = '';
    if (child.stdout) child.stdout.on('data', (chunk) => { stdout += chunk; });
    if (child.stderr) child.stderr.on('data', (chunk) => { stderr += chunk; });
    let timer;
    if (options.timeout) timer = setTimeout(() => child.kill('SIGTERM'), options.timeout);
    child.once('error', rejectProcess);
    child.once('close', (code, signal) => {
      if (timer) clearTimeout(timer);
      if (code === 0) resolveProcess({ stdout, stderr });
      else rejectProcess(new Error(`${command} ${args.join(' ')} exited with ${code ?? signal}${stderr ? `\n${stderr}` : ''}`));
    });
  });
}

function parseArgs(argv) {
  const values = {
    base: null,
    head: 'worktree',
    stories: 'all',
    widths: DEFAULT_WIDTHS,
    buildCmd: DEFAULT_BUILD_COMMAND,
    appDir: DEFAULT_APP_DIR,
    env: {},
    out: null,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help' || argument === '-h') return { help: true };
    if (!argument.startsWith('--')) throw new Error(`unknown argument: ${argument}`);
    const raw = argument.slice(2);
    const separator = raw.indexOf('=');
    const key = separator === -1 ? raw : raw.slice(0, separator);
    const inlineValue = separator === -1 ? undefined : raw.slice(separator + 1);
    let value = inlineValue;
    if (value === undefined) {
      value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error(`missing value for --${key}`);
      index += 1;
    }
    if (key === 'env') {
      const separator = value.indexOf('=');
      if (separator < 1) throw new Error('--env expects KEY=VALUE');
      const name = value.slice(0, separator);
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) throw new Error(`invalid environment variable name: ${name}`);
      values.env[name] = value.slice(separator + 1);
    } else if (key === 'widths') {
      values.widths = value.split(',').map((width) => Number(width.trim()));
      if (!values.widths.length || values.widths.some((width) => !Number.isInteger(width) || width < 1)) {
        throw new Error('--widths expects positive integers');
      }
    } else if (key === 'build-cmd') values.buildCmd = value;
    else if (key === 'app-dir') values.appDir = value;
    else if (key === 'base') values.base = value;
    else if (key === 'head') values.head = value;
    else if (key === 'stories') values.stories = value;
    else if (key === 'out') values.out = value;
    else throw new Error(`unknown argument: --${key}`);
  }
  return values;
}

function usage() {
  return [
    'Usage: node scripts/capture.mjs --out <dir>',
    '[--base <ref>] [--head <ref|worktree>] [--stories <id,id|all>]',
    '[--widths <csv>] [--build-cmd <command>] [--app-dir <dir>]',
    '[--env KEY=VALUE]',
  ].join(' ');
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const args = parseArgs(process.argv.slice(2));
    if (args.help) {
      console.log(usage());
    } else {
      if (!args.out) throw new Error(usage());
      await capture(args);
      console.log(`wrote captures to ${resolve(args.out)}`);
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  }
}
