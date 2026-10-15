import { readFileSync } from 'node:fs';

function findPenpotUrl(node) {
  if (!node || typeof node !== 'object') return null;
  if (node.penpot?.url) return node.penpot.url;
  for (const value of Object.values(node)) {
    const url = findPenpotUrl(value);
    if (url) return url;
  }
  return null;
}

async function rpc(url, sessionId, body) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      accept: 'application/json, text/event-stream',
      ...(sessionId ? { 'mcp-session-id': sessionId } : {}),
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(20000),
  });
  const text = await response.text();
  const json = text.startsWith('{')
    ? text
    : text.split('\n').filter((line) => line.startsWith('data:')).map((line) => line.slice(5)).pop();
  return { sessionId: response.headers.get('mcp-session-id') ?? sessionId, message: json ? JSON.parse(json) : null };
}

export async function probePenpot() {
  const url = findPenpotUrl(JSON.parse(readFileSync(`${process.env.HOME}/.claude.json`, 'utf8')));
  if (!url) return { ok: false, reason: 'no penpot MCP server in ~/.claude.json' };
  try {
    const init = await rpc(url, null, {
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'penpot-probe', version: '1' } },
    });
    await rpc(url, init.sessionId, { jsonrpc: '2.0', method: 'notifications/initialized' });
    const call = await rpc(url, init.sessionId, {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: { name: 'execute_code', arguments: { code: 'return penpot.currentFile?.name ?? null;' } },
    });
    const text = call.message?.result?.content?.map((part) => part.text).join(' ') ?? JSON.stringify(call.message?.error);
    return call.message?.result && !call.message.result.isError && !text.includes('Tool execution failed')
      ? { ok: true, reason: text }
      : { ok: false, reason: text };
  } catch (error) {
    return { ok: false, reason: error.cause?.code ?? error.message };
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const result = await probePenpot();
  console.log(`${result.ok ? 'ok' : 'down'}: ${result.reason}`);
  process.exit(result.ok ? 0 : 1);
}
