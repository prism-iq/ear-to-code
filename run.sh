#!/bin/bash
# ear-to-code launcher
cd "$(dirname "$0")"

# Activate venv if exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run with system audio capture by default
python3 ear.py --system "$@"
