#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the app root (where your main.py, models, services are)
APP_ROOT="/app"

# Find libmagic.so and set LD_LIBRARY_PATH
LIBMAGIC_DIR=$(find /nix/store -type f -name 'libmagic.so*' 2>/dev/null | head -n 1 | xargs dirname)
export LD_LIBRARY_PATH="${LIBMAGIC_DIR}:${LD_LIBRARY_PATH}"

# Source Nix profile for general environment setup
source /root/.nix-profile/etc/profile.d/nix.sh

# Activate Python virtual environment
source "${APP_ROOT}/.venv/bin/activate"

# Explicitly add app root to Python path
export PYTHONPATH="${APP_ROOT}:${PYTHONPATH}"

# --- Add more debug prints to check shell environment ---
echo "DEBUG: Current Working Directory (CWD): $(pwd)"
echo "DEBUG: PYTHONPATH environment variable: ${PYTHONPATH}"
echo "DEBUG: LD_LIBRARY_PATH environment variable: ${LD_LIBRARY_PATH}"
echo "DEBUG: PATH environment variable: ${PATH}" # NEW: Print PATH
echo "DEBUG: About to run uvicorn as a Python module..."
# --------------------------------------------------------

# Change this line:
# uvicorn main:app --app-dir "${APP_ROOT}" --host 0.0.0.0 --port "$PORT"

# To this:
python -m uvicorn main:app --app-dir "${APP_ROOT}" --host 0.0.0.0 --port "$PORT"