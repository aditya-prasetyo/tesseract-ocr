@echo off
setlocal enabledelayedexpansion

rem ==============================================
rem Run start.sh with Git Bash; fallback to WSL only if a distro exists
rem ==============================================

cd /d "%~dp0"

set NOPAUSE=
if /i "%~1"=="/nopause" set NOPAUSE=1

set "BASH_EXE="

rem 1) Cek lokasi umum Git Bash / MSYS / Cygwin terlebih dulu
if exist "%ProgramFiles%\Git\bin\bash.exe"         set "BASH_EXE=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH_EXE if exist "%ProgramFiles%\Git\usr\bin\bash.exe"  set "BASH_EXE=%ProgramFiles%\Git\usr\bin\bash.exe"
if not defined BASH_EXE if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "BASH_EXE=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not defined BASH_EXE if exist "C:\msys64\usr\bin\bash.exe"           set "BASH_EXE=C:\msys64\usr\bin\bash.exe"
if not defined BASH_EXE if exist "C:\cygwin64\bin\bash.exe"             set "BASH_EXE=C:\cygwin64\bin\bash.exe"

rem 2) Jika belum ketemu, cari di PATH tapi abaikan WindowsApps\bash.exe
if not defined BASH_EXE (
  for /f "usebackq delims=" %%I in (`where bash 2^>nul`) do (
    echo %%I | findstr /i "\\WindowsApps\\bash.exe" >nul
    if errorlevel 1 (
      set "BASH_EXE=%%~fI"
      goto :FOUND_BASH
    )
  )
)

:FOUND_BASH
if defined BASH_EXE (
  echo [INFO] Using Git/MSYS bash: "%BASH_EXE%"
  "%BASH_EXE%" -lc "./start.sh"
  set "ERR=%ERRORLEVEL%"
  goto :AFTER_RUN
)

rem 3) Fallback ke WSL HANYA jika ada distro
set "HASWSL="
where wsl >nul 2>nul
if "%ERRORLEVEL%"=="0" (
  for /f "usebackq delims=" %%D in (`wsl -l -q 2^>nul`) do (
    set HASWSL=1
    goto :DO_WSL
  )
)
goto :NO_BASH

:DO_WSL
if defined HASWSL (
  echo [INFO] Using WSL bash.
  wsl bash -lc "./start.sh"
  set "ERR=%ERRORLEVEL%"
  goto :AFTER_RUN
)

:NO_BASH
echo [ERROR] Tidak menemukan Git Bash/MSYS/Cygwin, dan WSL tidak punya distro.
echo         Instal Git for Windows (https://git-scm.com/download/win) atau install WSL distro:
echo         wsl --list --online   ^&   wsl --install <DistroName>
set "ERR=9009"
goto :AFTER_RUN

:AFTER_RUN
if "%ERR%"=="0" (
  echo [OK] start.sh selesai tanpa error.
) else (
  echo [FAIL] start.sh gagal dengan exit code %ERR%.
)

if not defined NOPAUSE pause
exit /b %ERR%
