@echo off
cd /d "%~dp0web"
where python >nul 2>nul
if not errorlevel 1 (
  python tools\launch.py
) else (
  py -3 tools\launch.py
)
pause
