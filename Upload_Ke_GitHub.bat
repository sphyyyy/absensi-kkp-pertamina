@echo off
title Upload Proyek Absensi ke GitHub
color 0B
echo =================================================================
echo         OTOMATISASI UPLOAD PROYEK KE GITHUB (VERCEL READY)
echo =================================================================
echo.
cd /d "%~dp0"

echo [1/3] Memeriksa konfigurasi dan status Git di folder ini...
git config --global user.email "sphyyy@gmail.com" >nul 2>&1
git config --global user.name "sphyyy" >nul 2>&1

if not exist ".git" (
    echo [*] Inisialisasi Git repository baru...
    git init
)

echo.
echo [2/3] Menyiapkan seluruh file proyek...
git add .
git commit -m "Siap deploy ke Vercel dan PostgreSQL Cloud" >nul 2>&1
git branch -M main

echo.
echo =================================================================
echo PENTING: Sebelum melanjutkan, pastikan Anda sudah membuat
echo Repository baru di GitHub.com dan menyalin URL-nya.
echo Contoh URL: https://github.com/username-anda/absensi-kkp.git
echo =================================================================
echo.
set /p REPO_URL="Masukkan / Paste URL Repository GitHub Anda di sini: "

if "%REPO_URL%"=="" (
    echo [!] URL tidak boleh kosong. Dibatalkan.
    pause
    exit /b
)

echo.
echo [3/3] Menghubungkan dan meng-upload (push) ke GitHub...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git push -u origin main --force

echo.
echo =================================================================
if %errorlevel% equ 0 (
    echo  ✅ UPLOAD BERHASIL! Proyek Anda sudah masuk ke GitHub. ✅
    echo  Sekarang buka Vercel.com dan klik 'Import' repository tersebut.
) else (
    echo  ❌ UPLOAD GAGAL! Pastikan URL benar atau Anda sudah login Git di laptop.
)
echo =================================================================
pause
