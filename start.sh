#!/usr/bin/env bash
# =========================
# start.sh
# Simple launcher untuk start.py
# =========================

set -euo pipefail

# Pindah ke direktori script ini
cd "$(dirname "$0")"

# --- Pilih python (python3 > python)
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "[ERROR] Python tidak ditemukan di PATH." >&2
    exit 1
fi

# --- Jalankan start.py dengan semua argumen
exec "$PY" start.py "$@"