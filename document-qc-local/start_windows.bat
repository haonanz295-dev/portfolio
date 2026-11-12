@echo off
cd /d "%~dp0"
python document_qc_offline_ocr.py
if errorlevel 1 pause
