#!/usr/bin/env bash
set -u
while IFS= read -r line; do
  name=${line#export }
  name=${name%%=*}
  [[ -v $name ]] || eval "$line" >/dev/null 2>&1
done < <(grep '^export PENPOT_[A-Z_]*=' "$HOME/.bashrc" 2>/dev/null)
for name in PENPOT_URL PENPOT_FLYT_FILE PENPOT_AGENT_ENV; do
  if [[ -z ${!name:-} ]]; then
    echo "$name must be set in the environment or ~/.bashrc" >&2
    exit 1
  fi
done
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
echo "penpot still down; check PENPOT_URL and $STATE/keepalive.log"
exit 1
