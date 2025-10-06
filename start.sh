#!/usr/bin/env bash
set -euo pipefail

# =========================
# start.sh
# - Buat/aktifkan venv
# - Pastikan Poppler (pdf2image)
# - Install requirements
# - Jalankan pdf_processor.py (+ forward argumen)
# =========================

# Pindah ke direktori skrip ini (agar path relatif aman)
cd "$(dirname "$0")"

# --- Detect platform (untuk hint Poppler Windows)
UNAME="$(uname -s || echo unknown)"
IS_WIN=0
case "$UNAME" in
 ( MINGW*|MSYS*|CYGWIN*) IS_WIN=1 ;;
esac

# --- Pilih python (python3 > python)
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[ERROR] Python tidak ditemukan di PATH." >&2
  exit 1
fi

# --- Siapkan venv
if [ ! -d "env" ]; then
  echo "[INFO] Membuat virtualenv: ./env"
  "$PY" -m venv env
fi

# --- Aktivasi venv (Windows Git Bash vs Unix/Mac)
if [ -f "env/Scripts/activate" ]; then
  # shellcheck disable=SC1091
  source "env/Scripts/activate"
elif [ -f "env/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "env/bin/activate"
else
  echo "[ERROR] Virtualenv korup/tidak lengkap. Hapus folder env lalu jalankan ulang." >&2
  exit 1
fi

# --- (Opsional) load .env
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source ./.env
  set +a
fi

# --- Pastikan Poppler (untuk pdf2image)
# 1) Bila POPPLER_PATH di .env atau environment, masukkan ke PATH
if [ "${POPPLER_PATH:-}" != "" ]; then
  export PATH="$POPPLER_PATH:$PATH"
fi
# 2) Windows Git Bash: coba path umum Poppler jika belum ada pdftoppm
if ! command -v pdftoppm >/dev/null 2>&1; then
  if [ "$IS_WIN" -eq 1 ]; then
    # Coba lokasi instalasi umum Poppler; ubah bila perlu
    for P in "/c/Program Files/poppler/bin" "/c/poppler/bin" "/c/Users/Public/poppler/bin"; do
      if [ -d "$P" ]; then
        export PATH="$P:$PATH"
        break
      fi
    done
  fi
fi
# 3) Validasi terakhir
if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "[WARN] 'pdftoppm' (Poppler) tidak ditemukan di PATH."
  echo "       pdf2image butuh Poppler. Install & tambahkan folder 'bin' ke PATH"
  echo "       (Windows contoh: C:\\Program Files\\poppler\\bin)."
fi

# --- Upgrade pip toolchain
python -m pip install --upgrade pip wheel setuptools >/dev/null

# --- Install dependencies (jika ada)
if [ -f "dependencies/requirements.txt" ]; then
  echo "[INFO] Menginstal dependencies dari requirements.txt"
  pip install -r dependencies/requirements.txt
else
  echo "[INFO] requirements.txt tidak ditemukan, lewati instalasi."
fi

# --- Jalankan program utama; teruskan semua argumen: ./start.sh --foo bar
echo "[INFO] Membuat input/ jika belum ada"
mkdir -p input
echo "[INFO] Menjalankan: pdf_processor.py $*"
exec python pdf_processor.py "$@"
