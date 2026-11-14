#!/usr/bin/env bash
# IN THIS CONTAINER. Forwards 127.0.0.1:8000 here to 127.0.0.1:8000 on the GPU box over SSH. The model server is
# never reachable from the internet; the code under review travels only inside this SSH connection.
#
#   VERDA_HOST=<ip> scripts/selfhost/tunnel.sh        # foreground; Ctrl-C closes it
#   VERDA_HOST=<ip> scripts/selfhost/tunnel.sh -f     # background (ssh -f); close with: pkill -f 'ssh .*8000:127.0.0.1:8000'
set -euo pipefail
: "${VERDA_HOST:?set VERDA_HOST to the box IP (from the board)}"
KEY="${VERDA_KEY:-/data/work/ssh/verda}"
exec ssh -i "$KEY" -N "$@" \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new \
  -L 127.0.0.1:8000:127.0.0.1:8000 "${VERDA_USER:-root}@$VERDA_HOST"
