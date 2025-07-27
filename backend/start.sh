#!/bin/bash

set -e

APP_ROOT="/app"

LIBMAGIC_DIR=$(find /nix/store -type f -name 'libmagic.so*' 2>/dev/null | head -n 1 | xargs dirname)
export LD_LIBRARY_PATH="${LIBMAGIC_DIR}:${LD_LIBRARY_PATH}"

source /root/.nix-profile/etc/profile.d/nix.sh
source "${APP_ROOT}/.venv/bin/activate"

# We will let Uvicorn handle PYTHONPATH more directly by running from the correct dir
export PYTHONPATH="${APP_ROOT}:${PYTHONPATH}" # Keep this, good practice

echo "DEBUG: Current Working Directory (CWD): $(pwd)"
echo "DEBUG: PYTHONPATH environment variable: ${PYTHONPATH}"
echo "DEBUG: LD_LIBRARY_PATH environment variable: ${LD_LIBRARY_PATH}"
echo "DEBUG: PATH environment variable: ${PATH}"
echo "DEBUG: About to run uvicorn as a Python module..."

# --- NEW UVICORN INVOCATION ---
# Change directory to APP_ROOT first, then run uvicorn
# This removes ambiguity about where 'main' is found and its relation to other packages.
cd "${APP_ROOT}"

# Run uvicorn from within the /app directory
# We remove --app-dir as we are already in the directory.
python -m uvicorn main:app --host 0.0.0.0 --port "$PORT"