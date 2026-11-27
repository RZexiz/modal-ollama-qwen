#!/bin/bash
# deploy.sh — runs on the VPS (mesin 1) via the task board.
# Usage: bash deploy.sh <modal-token-id> <modal-token-secret>
# Installs the Modal CLI if missing, sets the token, deploys the app.
set -e
cd "$(dirname "$0")"

TOKEN_ID="$1"
TOKEN_SECRET="$2"
if [ -z "$TOKEN_ID" ] || [ -z "$TOKEN_SECRET" ]; then
  echo "usage: bash deploy.sh <token-id> <token-secret>" >&2
  exit 2
fi

if ! command -v modal >/dev/null 2>&1; then
  echo "installing modal CLI ..."
  python3 -m pip install --break-system-packages modal 2>/dev/null \
    || python3 -m pip install modal \
    || pip install modal
fi

echo "setting modal token (profile romansyah) ..."
modal token set --token-id "$TOKEN_ID" --token-secret "$TOKEN_SECRET" \
  --profile=romansyah --no-verify

echo "deploying ..."
modal --profile romansyah deploy app.py

echo "DEPLOY_DONE"
modal --profile romansyah app list 2>&1 | head -20
