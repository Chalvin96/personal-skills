#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
STATE="${XDG_STATE_HOME:-$HOME/.local/state}/penpot-bot"
mkdir -p "$STATE"
node probe.mjs && exit 0
echo "restarting bot browser"
[ -f "$STATE/keepalive.pid" ] && kill "$(cat "$STATE/keepalive.pid")" 2>/dev/null
sleep 2
nohup setsid node keepalive.mjs >> "$STATE/keepalive.log" 2>&1 &
echo $! > "$STATE/keepalive.pid"
for _ in $(seq 12); do
  sleep 10
  node probe.mjs && exit 0
done
echo "penpot still down; check $PENPOT_URL and $STATE/keepalive.log"
exit 1
