#!/usr/bin/env python3
"""
start.py
- Buat/aktifkan venv
- Pastikan Poppler (pdf2image)
- Install requirements
- Jalankan pdf_processor.py (+ forward argumen)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def main():
    """Main startup function"""
    
    # Pindah ke direktori script ini
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("=" * 70)
    print("Starting PDF Processor Setup")
    print("=" * 70)
    print()
    
    # --- Detect platform
    is_windows = platform.system() == "Windows"
    is_mac = platform.system() == "Darwin"
    is_linux = platform.system() == "Linux"
    
    # --- Pilih python (gunakan yang sedang menjalankan script ini)
    current_python = sys.executable
    print(f"[INFO] Python: {current_python}")
    print(f"[INFO] Platform: {platform.system()}")
    print()
    
    # --- Siapkan venv
    venv_dir = script_dir / "env"
    
    if not venv_dir.exists():
        print("[INFO] Membuat virtualenv: ./env")
        try:
            subprocess.run([current_python, "-m", "venv", "env"], check=True)
            print("[INFO] Virtualenv berhasil dibuat.")
        except subprocess.CalledProcessError:
            print("[ERROR] Gagal membuat virtualenv.")
            sys.exit(1)
        print()
    
    # --- Tentukan path python di venv
    if is_windows:
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_activate = venv_dir / "Scripts" / "activate"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_activate = venv_dir / "bin" / "activate"
    
    if not venv_python.exists():
        print("[ERROR] Virtualenv korup/tidak lengkap.")
        print("        Hapus folder 'env' lalu jalankan ulang.")
        sys.exit(1)
    
    print(f"[INFO] Virtualenv: {venv_python}")
    print()
    
    # --- Load .env (opsional)
    env_file = script_dir / ".env"
    if env_file.exists():
        print("[INFO] Loading .env file...")
        load_env_file(env_file)
        print("[INFO] .env file loaded.")
        print()
    
    # --- Pastikan Poppler (untuk pdf2image)
    setup_poppler(is_windows, is_mac, is_linux)
    
    # --- Upgrade pip toolchain
    print("[INFO] Upgrade pip, wheel, setuptools...")
    try:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print("[INFO] pip toolchain berhasil diupgrade.")
    except subprocess.CalledProcessError:
        print("[WARN] Gagal upgrade pip toolchain (mungkin sudah terbaru).")
    print()
    
    # --- Install dependencies (jika ada)
    req_file = script_dir / "dependencies" / "requirements.txt"
    if req_file.exists():
        print("[INFO] Menginstal dependencies dari requirements.txt...")
        try:
            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-r", str(req_file)],
                check=True
            )
            print("[INFO] Dependencies berhasil diinstal.")
        except subprocess.CalledProcessError:
            print("[ERROR] Gagal menginstal dependencies.")
            sys.exit(1)
    else:
        print("[INFO] requirements.txt tidak ditemukan, lewati instalasi.")
    print()
    
    # --- Buat folder input jika belum ada
    input_dir = script_dir / "input"
    input_dir.mkdir(exist_ok=True)
    print(f"[INFO] Folder input: {input_dir}")
    print()
    
    # --- Jalankan program utama dengan semua argumen
    print("=" * 70)
    print(f"[INFO] Menjalankan: pdf_processor.py {' '.join(sys.argv[1:])}")
    print("=" * 70)
    print()
    
    # Jalankan pdf_processor.py dengan argumen yang sama
    try:
        result = subprocess.run(
            [str(venv_python), "pdf_processor.py"] + sys.argv[1:],
            check=False
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan oleh user.")
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan pdf_processor.py: {e}")
        sys.exit(1)


def load_env_file(env_path):
    """Load environment variables dari file .env"""
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip komentar dan baris kosong
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Hapus quotes jika ada
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
    except Exception as e:
        print(f"[WARN] Gagal load .env file: {e}")


def setup_poppler(is_windows, is_mac, is_linux):
    """Setup Poppler PATH"""
    
    # 1) Bila POPPLER_PATH di .env atau environment, masukkan ke PATH
    poppler_path = os.environ.get('POPPLER_PATH', '')
    if poppler_path:
        print(f"[INFO] POPPLER_PATH ditemukan: {poppler_path}")
        os.environ['PATH'] = f"{poppler_path}{os.pathsep}{os.environ['PATH']}"
    
    # 2) Cek apakah pdftoppm sudah tersedia
    if check_command('pdftoppm'):
        print("[INFO] Poppler ditemukan: pdftoppm tersedia.")
        print()
        return
    
    # 3) Windows: coba path umum Poppler
    if is_windows:
        print("[INFO] Mencari Poppler di lokasi umum Windows...")
        common_paths = [
            r"C:\Program Files\poppler\bin",
            r"C:\Program Files (x86)\poppler\bin",
            r"C:\poppler\bin",
            r"C:\Users\Public\poppler\bin",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                print(f"[INFO] Poppler ditemukan di: {path}")
                os.environ['PATH'] = f"{path}{os.pathsep}{os.environ['PATH']}"
                if check_command('pdftoppm'):
                    print("[INFO] Poppler berhasil ditambahkan ke PATH.")
                    print()
                    return
                break
    
    # 4) Validasi terakhir
    if not check_command('pdftoppm'):
        print()
        print("[WARN] " + "=" * 60)
        print("[WARN] 'pdftoppm' (Poppler) tidak ditemukan di PATH.")
        print("[WARN] pdf2image membutuhkan Poppler untuk bekerja.")
        print("[WARN]")
        
        if is_windows:
            print("[WARN] Download Poppler untuk Windows dari:")
            print("[WARN] https://github.com/oschwartz10612/poppler-windows/releases")
            print("[WARN]")
            print("[WARN] Ekstrak dan tambahkan folder 'bin' ke PATH")
            print("[WARN] Contoh: C:\\Program Files\\poppler\\bin")
        elif is_mac:
            print("[WARN] Install Poppler dengan Homebrew:")
            print("[WARN] brew install poppler")
        elif is_linux:
            print("[WARN] Install Poppler dengan package manager:")
            print("[WARN] Ubuntu/Debian: sudo apt-get install poppler-utils")
            print("[WARN] Fedora: sudo dnf install poppler-utils")
        
        print("[WARN] " + "=" * 60)
        print()


def check_command(cmd):
    """Cek apakah command tersedia di PATH"""
    try:
        subprocess.run(
            [cmd, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5
        )
        return True
    except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan oleh user.")
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)