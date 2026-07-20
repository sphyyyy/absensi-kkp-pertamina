@echo off
title Cloudflare HTTPS Tunnel - Sistem Absensi KKP
echo Mengaktifkan HTTPS Tunnel untuk Akses Smartphone...
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" run_tunnel.py
pause
