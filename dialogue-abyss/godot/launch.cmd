@echo off
setlocal
where godot >nul 2>nul
if errorlevel 1 (
  echo Open project.godot in your installed Godot 4 editor, then press F5.
  echo This folder is a migration foundation. Use the parent Launch.cmd for the full Web demo.
  pause
  exit /b 1
)
godot --path "%~dp0" --editor
