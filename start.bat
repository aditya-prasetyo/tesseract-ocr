@echo off
REM =========================
REM start.bat
REM Simple launcher untuk start.py
REM =========================

REM Pindah ke direktori script ini
cd /d "%~dp0"

REM --- Cari Python
set PY=
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY=python
) else (
    where python3 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PY=python3
    ) else (
        echo [ERROR] Python tidak ditemukan di PATH.
        echo        Install Python dari https://www.python.org/downloads/
        echo        Pastikan checklist "Add Python to PATH" saat install.
        pause
        exit /b 1
    )
)

REM --- Jalankan start.py dengan semua argumen
%PY% start.py %*

REM --- Simpan exit code
set EXITCODE=%ERRORLEVEL%

REM --- Pause jika ada error atau dijalankan via double-click
if %EXITCODE% NEQ 0 (
    echo.
    echo [ERROR] Program selesai dengan error code: %EXITCODE%
    pause
) else (
    REM Pause hanya jika dijalankan via double-click
    echo %CMDCMDLINE% | findstr /i /c:"/c" >nul && (
        echo.
        echo [INFO] Program selesai dengan sukses.
        pause
    )
)

exit /b %EXITCODE%