import { readFileSync } from 'node:fs';
import { probePenpot } from './probe.mjs';
import { chromium } from 'playwright';

const BASE = process.env.PENPOT_URL;
const FILE = process.env.PENPOT_FLYT_FILE;
if (!BASE || !FILE) throw new Error('PENPOT_URL and PENPOT_FLYT_FILE must be set');
const env = Object.fromEntries(
  readFileSync(process.env.PENPOT_AGENT_ENV, 'utf8')
    .split('\n')
    .filter((line) => line.includes('='))
    .map((line) => [line.slice(0, line.indexOf('=')), line.slice(line.indexOf('=') + 1)]),
);
const log = (message) => console.log(`${new Date().toISOString()} ${message}`);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function openFile(context) {
  const page = await context.newPage();
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.goto(`${BASE}/#/auth/login`);
  await sleep(4000);
  if (page.url().includes('login')) {
    await page.fill('#email', env.PENPOT_EMAIL);
    await page.fill('#password', env.PENPOT_PASSWORD);
    await page.keyboard.press('Enter');
    await sleep(5000);
  }
  await page.goto(FILE);
  await sleep(15000);
  log(`opened: ${await page.title()}`);
  return page;
}

async function healthy(page) {
  if (page.isClosed()) return false;
  try {
    const title = await page.title();
    if (!title.startsWith('Design System')) return false;
    const probe = await probePenpot();
    if (!probe.ok) log(`probe failed: ${probe.reason}`);
    return probe.ok;
  } catch {
    return false;
  }
}

const browser = await chromium.launch({ headless: true, args: ['--remote-debugging-port=9333'] });
const context = await browser.newContext();
await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: BASE });
let page = await openFile(context);
for (;;) {
  await sleep(60000);
  if (!(await healthy(page))) {
    log('tab unhealthy, reopening');
    await page.close().catch(() => {});
    page = await openFile(context).catch((error) => {
      log(`reopen failed: ${error.message}`);
      return page;
    });
  }
}
