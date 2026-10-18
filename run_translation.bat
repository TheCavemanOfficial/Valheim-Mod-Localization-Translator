@echo off
title Valheim Mod Localization Translator
cd /d "%~dp0"
echo ========================================================
echo        Valheim Mod Localization Translator Tool         
echo ========================================================
echo.
set SCRIPT=mod_localization_translator.py
if not exist "%SCRIPT%" set SCRIPT=pov_auto_translate.py

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%SCRIPT%"
    goto done
)
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py "%SCRIPT%"
    goto done
)

echo [ERROR] Python was not found on your system!
echo.
echo To run this tool, please install Python 3:
echo   1. Download from https://www.python.org/downloads/ (or Microsoft Store)
echo   2. IMPORTANT: During installation, make sure to check:
echo      [x] "Add Python to PATH"
echo.
:done
pause

