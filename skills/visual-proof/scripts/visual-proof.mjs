import { spawn } from 'node:child_process';
import { resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

async function runStep(script, args) {
  await new Promise((resolveStep, rejectStep) => {
    const child = spawn(process.execPath, [script, ...args], { stdio: 'inherit' });
    child.once('error', rejectStep);
    child.once('close', (code, signal) => {
      if (code === 0) resolveStep();
      else rejectStep(new Error(`${script} exited with ${code ?? signal}`));
    });
  });
}

function splitPageArgs(argv) {
  const captureArgs = [];
  const pageArgs = [];
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--serve') {
      pageArgs.push(argument);
    } else if (argument === '--port' || argument === '--host') {
      pageArgs.push(argument, argv[index + 1]);
      index += 1;
    } else if (argument.startsWith('--port=') || argument.startsWith('--host=')) {
      pageArgs.push(argument);
    } else {
      captureArgs.push(argument);
    }
  }
  return { captureArgs, pageArgs };
}

function valueFor(args, name) {
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === `--${name}`) return args[index + 1];
    if (args[index].startsWith(`--${name}=`)) return args[index].slice(name.length + 3);
  }
  return null;
}

function usage() {
  return 'Usage: node scripts/visual-proof.mjs --out <dir> [capture options] [--serve] [--port <port>] [--host <host>]';
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const argv = process.argv.slice(2);
    if (argv.includes('--help') || argv.includes('-h')) {
      console.log(usage());
    } else {
      const { captureArgs, pageArgs } = splitPageArgs(argv);
      const out = valueFor(captureArgs, 'out');
      if (!out) throw new Error(usage());
      const scriptDir = new URL('.', import.meta.url);
      await runStep(fileURLToPath(new URL('capture.mjs', scriptDir)), captureArgs);
      await runStep(fileURLToPath(new URL('diff.mjs', scriptDir)), [
        '--before', resolve(out, 'before'),
        '--after', resolve(out, 'after'),
        '--out', resolve(out),
      ]);
      await runStep(fileURLToPath(new URL('page.mjs', scriptDir)), ['--out', resolve(out), ...pageArgs]);
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  }
}
