# Sistem Absensi KKP — PT. Pertamina Patra Niaga Regional Sulawesi

Sistem absensi digital berbasis web untuk mahasiswa magang menggunakan Python Flask dengan rancangan UI *Glassmorphism*, dilengkapi deteksi lokasi GPS & pembatasan radius absen (*Geofencing*). Mendukung *deployment* Serverless di Vercel + PostgreSQL.

## 🌟 Fitur Utama
- 📍 **GPS Geofence Validation**: Pembatasan area absensi mahasiswa berdasarkan radius koordinat kantor (Real-time).
- ⏰ **Dynamic Time Windows**: Pengaturan jam masuk, pulang, dan batas keterlambatan secara dinamis via Dashboard Admin.
- 👥 **Role-Based Access (RBAC)**: Hak akses spesifik untuk Admin, Dosen, dan Mahasiswa Magang.
- 📊 **Dashboard & Laporan**: Export riwayat absensi ke **Excel (.xlsx)** & **PDF**, serta fitur impor data mahasiswa massal via Excel.
- ☁️ **Cloud Ready**: Siap deploy ke Vercel dengan *auto-seed* PostgreSQL.

## 🛠️ Tech Stack
- **Backend**: Python 3.12+, Flask, SQLAlchemy ORM
- **Frontend**: Bootstrap 5, UI Glassmorphism, Vanilla JS, SweetAlert2
- **Database**: SQLite (Lokal) / PostgreSQL Cloud (Production)

## 🚀 Quick Start (Local Development)

```bash
git clone https://github.com/sphyyyy/absensi-kkp-pertamina.git
cd absensi-kkp-pertamina

# Buat & Aktifkan Virtual Environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install Dependensi
pip install -r requirements.txt

# Inisialisasi Database (Auto-Migrate)
python seed.py

# Jalankan Server (Akses di http://localhost:5000)
python run.py
```

## 🔑 Akun Default (Siap Pakai)
Setelah menjalankan `seed.py`, Anda dapat login menggunakan akun berikut:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Dosen** | `dosen1` | `dosen123` |
| **Mahasiswa** | `mhs1` | `mhs123` |

## ☁️ Deployment Instan (Vercel)
Aplikasi dirancang **100% Serverless Ready**. 
1. Buat database di **Neon.tech / Supabase** dan dapatkan `DATABASE_URL`.
2. Push repository ini ke GitHub.
3. Import project di [Vercel.com](https://vercel.com).
4. Masukkan Environment Variable `DATABASE_URL` dengan Connection String PostgreSQL Anda.
5. Deploy. Sistem akan otomatis membangun dan mengisi tabel database.