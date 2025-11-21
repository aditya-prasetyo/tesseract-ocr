@echo off
setlocal enabledelayedexpansion

REM =========================
REM start.bat
REM - Buat/aktifkan venv
REM - Pastikan Poppler (pdf2image)
REM - Install requirements
REM - Jalankan pdf_processor.py (+ forward argumen)
REM =========================

REM Pindah ke direktori script ini
cd /d "%~dp0"

echo ========================================
echo Starting PDF Processor Setup
echo ========================================
echo.

REM --- Pilih python (python3 > python)
set PY=
where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY=python3
    echo [INFO] Python ditemukan: python3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PY=python
        echo [INFO] Python ditemukan: python
    ) else (
        echo [ERROR] Python tidak ditemukan di PATH.
        echo        Install Python dan tambahkan ke PATH.
        pause
        exit /b 1
    )
)

REM --- Siapkan venv
if not exist "env" (
    echo [INFO] Membuat virtualenv: .\env
    %PY% -m venv env
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Gagal membuat virtualenv.
        pause
        exit /b 1
    )
    echo [INFO] Virtualenv berhasil dibuat.
    echo.
)

REM --- Aktivasi venv
if exist "env\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan virtualenv...
    call env\Scripts\activate.bat
) else (
    echo [ERROR] Virtualenv korup/tidak lengkap.
    echo        Hapus folder 'env' lalu jalankan ulang.
    pause
    exit /b 1
)

REM --- Load .env (opsional)
if exist .env (
    echo [INFO] Loading .env file...
    for /f "usebackq tokens=*" %%a in (.env) do (
        set "line=%%a"
        REM Skip komentar dan baris kosong
        echo !line! | findstr /r "^#" >nul
        if errorlevel 1 (
            if not "!line!"=="" (
                REM Set environment variable
                for /f "tokens=1,2 delims==" %%b in ("!line!") do (
                    set "%%b=%%c"
                )
            )
        )
    )
    echo [INFO] .env file loaded.
    echo.
)

REM --- Pastikan Poppler (untuk pdf2image)
REM 1) Bila POPPLER_PATH di .env atau environment, masukkan ke PATH
if defined POPPLER_PATH (
    echo [INFO] POPPLER_PATH ditemukan: %POPPLER_PATH%
    set "PATH=%POPPLER_PATH%;%PATH%"
)

REM 2) Coba path umum Poppler jika belum ada pdftoppm
where pdftoppm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Mencari Poppler di lokasi umum...
    
    if exist "C:\Program Files\poppler\bin" (
        echo [INFO] Poppler ditemukan di: C:\Program Files\poppler\bin
        set "PATH=C:\Program Files\poppler\bin;%PATH%"
    ) else if exist "C:\Program Files (x86)\poppler\bin" (
        echo [INFO] Poppler ditemukan di: C:\Program Files (x86)\poppler\bin
        set "PATH=C:\Program Files (x86)\poppler\bin;%PATH%"
    ) else if exist "C:\poppler\bin" (
        echo [INFO] Poppler ditemukan di: C:\poppler\bin
        set "PATH=C:\poppler\bin;%PATH%"
    ) else if exist "C:\Users\Public\poppler\bin" (
        echo [INFO] Poppler ditemukan di: C:\Users\Public\poppler\bin
        set "PATH=C:\Users\Public\poppler\bin;%PATH%"
    )
)

REM 3) Validasi terakhir
where pdftoppm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARN] ================================================
    echo [WARN] 'pdftoppm' (Poppler) tidak ditemukan di PATH.
    echo [WARN] pdf2image membutuhkan Poppler untuk bekerja.
    echo [WARN] 
    echo [WARN] Download Poppler dari:
    echo [WARN] https://github.com/oschwartz10612/poppler-windows/releases
    echo [WARN] 
    echo [WARN] Ekstrak dan tambahkan folder 'bin' ke PATH
    echo [WARN] Contoh: C:\Program Files\poppler\bin
    echo [WARN] ================================================
    echo.
) else (
    echo [INFO] Poppler ditemukan: pdftoppm tersedia.
    echo.
)

REM --- Upgrade pip toolchain
echo [INFO] Upgrade pip, wheel, setuptools...
python -m pip install --upgrade pip wheel setuptools >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] pip toolchain berhasil diupgrade.
) else (
    echo [WARN] Gagal upgrade pip toolchain (mungkin sudah terbaru).
)
echo.

REM --- Install dependencies (jika ada)
if exist "dependencies\requirements.txt" (
    echo [INFO] Menginstal dependencies dari requirements.txt...
    pip install -r dependencies\requirements.txt
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Dependencies berhasil diinstal.
    ) else (
        echo [ERROR] Gagal menginstal dependencies.
        pause
        exit /b 1
    )
) else (
    echo [INFO] requirements.txt tidak ditemukan, lewati instalasi.
)
echo.

REM --- Buat folder input jika belum ada
if not exist "input" (
    echo [INFO] Membuat folder input\...
    mkdir input
)

REM --- Jalankan program utama dengan semua argumen
echo ========================================
echo [INFO] Menjalankan: pdf_processor.py %*
echo ========================================
echo.
python pdf_processor.py %*

REM Simpan exit code
set EXITCODE=%ERRORLEVEL%

REM --- TAMBAHKAN INI: Pause agar window tidak langsung close ---
echo.
echo ========================================
if %EXITCODE% EQU 0 (
    echo [INFO] Program selesai dengan sukses.
) else (
    echo [ERROR] Program selesai dengan error code: %EXITCODE%
)
echo ========================================
echo.
pause

endlocal
exit /b %EXITCODE%