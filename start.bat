@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

REM --- Cek Python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PY=python3
    ) else (
        echo [ERROR] Python tidak ditemukan di PATH.
        pause
        exit /b 1
    )
)

REM --- Buat venv
if not exist "env" (
    echo [INFO] Membuat virtualenv: .\env
    %PY% -m venv env
)

REM --- Aktivasi venv
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
) else (
    echo [ERROR] Virtualenv korup. Hapus folder env lalu jalankan ulang.
    pause
    exit /b 1
)

REM --- Load .env
if exist .env (
    echo [INFO] Loading .env file
    for /f "usebackq tokens=*" %%a in (.env) do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if not "!line!"=="" (
                set "%%a"
            )
        )
    )
)

REM --- Setup Poppler
if defined POPPLER_PATH (
    set PATH=%POPPLER_PATH%;%PATH%
)

where pdftoppm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Program Files\poppler\bin" (
        set PATH=C:\Program Files\poppler\bin;%PATH%
    ) else if exist "C:\poppler\bin" (
        set PATH=C:\poppler\bin;%PATH%
    )
)

where pdftoppm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] pdftoppm (Poppler) tidak ditemukan di PATH.
    echo        Install Poppler dan tambahkan ke PATH.
)

REM --- Upgrade pip
echo [INFO] Upgrade pip toolchain
python -m pip install --upgrade pip wheel setuptools >nul 2>&1

REM --- Install requirements
if exist "dependencies\requirements.txt" (
    echo [INFO] Menginstal dependencies dari requirements.txt
    pip install -r dependencies\requirements.txt
) else (
    echo [INFO] requirements.txt tidak ditemukan, lewati instalasi.
)

REM --- Buat folder input
if not exist "input" (
    echo [INFO] Membuat input/
    mkdir input
)

REM --- Jalankan program
echo [INFO] Menjalankan: pdf_processor.py %*
python pdf_processor.py %*

endlocal