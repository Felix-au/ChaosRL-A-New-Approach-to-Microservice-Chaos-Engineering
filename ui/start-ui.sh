#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo "ChaosRL Presentation UI Launcher"
echo "========================================================"

echo "[1/2] Verifying and updating data bundle..."
python3 scripts/build_data.py

echo "[2/2] Launching Presentation Web Server..."
npm run present

