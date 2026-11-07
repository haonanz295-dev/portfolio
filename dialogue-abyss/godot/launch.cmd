@echo off
setlocal
if not defined GODOT set "GODOT=godot"
"%GODOT%" --headless --path "%~dp0" --editor --import --quit
if errorlevel 1 (
 echo Install Godot 4.x and set GODOT to its executable, or open project.godot manually.
 pause
 exit /b 1
)
start "Dialogue Abyss Native" "%GODOT%" --path "%~dp0"
