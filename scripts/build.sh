#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd )/.."
cd "$PROJECT_ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install pyinstaller

pyinstaller --onefile \
    --add-data "pdf-generator/background.png:." \
    --name nuclearss-pdf \
    pdf-generator/main.py

pyinstaller --onefile \
    --add-data "seaker/patterns.json:." \
    --name nuclearss-seaker \
    seaker/src/main.py

pyinstaller --onefile \
    --name nuclearss \
    tui/src/main.py


DIST_DIR="${DIST_DIR:-dist}"

for bin_name in nuclearss-pdf nuclearss-seaker nuclearss; do
    if [ -f "${DIST_DIR}/${bin_name}" ]; then
        echo "Installing ${bin_name} to /usr/local/bin (may require sudo)..."
        sudo install -m 0755 "${DIST_DIR}/${bin_name}" /usr/local/bin/"${bin_name}"
    else
        echo "WARNING: ${DIST_DIR}/${bin_name} not found, skipping install." >&2
    fi
done

echo "Done."
