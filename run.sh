#!/usr/bin/env bash
# Turkish Dataset Builder — Startup Script
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install -q -r requirements.txt

python3 -m dataset_cleaner "$@"
