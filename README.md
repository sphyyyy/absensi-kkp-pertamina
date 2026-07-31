# Sistem Absensi KKP — PT. Pertamina Patra Niaga Regional Sulawesi

Sistem absensi digital berbasis web untuk mahasiswa magang (KKP) menggunakan **Python Flask**, dilengkapi validasi lokasi **GPS Geofencing** real-time dan desain antarmuka **Glassmorphism**. Mendukung deployment Serverless di **Vercel + PostgreSQL**.

## ✨ Fitur Utama

| Fitur | Deskripsi |
|:------|:----------|
| 📍 **GPS Geofencing** | Validasi lokasi absensi berdasarkan radius koordinat kantor secara real-time |
| ⏰ **Dynamic Time Windows** | Pengaturan jam masuk & pulang secara dinamis via Dashboard Admin |
| 👥 **Role-Based Access** | Hak akses spesifik untuk Admin, Dosen Pembimbing, dan Mahasiswa |
| 📊 **Laporan & Ekspor** | Export riwayat absensi ke **Excel (.xlsx)** dan **PDF** |
| 📥 **Import Massal** | Import data mahasiswa dari file Excel secara batch |
| ☁️ **Cloud Ready** | Siap deploy ke Vercel dengan auto-seed PostgreSQL |

## 🛠️ Tech Stack

| Layer | Teknologi |
|:------|:----------|
| **Backend** | Python 3.12+, Flask 3.0, SQLAlchemy ORM |
| **Frontend** | Bootstrap 5, Glassmorphism UI, Vanilla JS, SweetAlert2 |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **GPS** | Haversine Formula, Geofencing Validation |
| **Reports** | ReportLab (PDF), OpenPyXL (Excel) |

## 📁 Struktur Proyek

```
├── api/                    # Entry point Vercel Serverless
├── app/
│   ├── api/                # REST API endpoints
│   ├── attendance/         # Modul absensi (check-in/out)
│   ├── auth/               # Autentikasi & login
│   ├── dashboard/          # Dashboard per role
│   ├── models/             # Database models (User, Attendance, Setting, Log)
│   ├── services/           # Business logic layer
│   ├── static/             # CSS, JS, dan aset gambar
│   ├── templates/          # HTML templates (Jinja2)
│   └── utils/              # Helper, decorator, dan konstanta
├── tests/                  # Unit & integration tests
├── seed.py                 # Database seeder
├── run.py                  # Entry point lokal
└── vercel.json             # Konfigurasi deployment Vercel
```

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/sphyyyy/absensi-kkp-pertamina.git
cd absensi-kkp-pertamina

# Buat & aktifkan virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependensi
pip install -r requirements.txt

# Salin dan konfigurasi environment variables
cp .env.example .env

# Inisialisasi database
python seed.py

# Jalankan server development
python run.py
```

Akses di **http://localhost:5000**

## 🔑 Akun Default

| Role | Username | Password |
|:-----|:---------|:---------|
| Admin | `admin` | `admin123` |
| Dosen | `dosen1` | `dosen123` |
| Mahasiswa | `mhs1` | `mhs123` |

## ☁️ Deployment (Vercel)

1. Buat database PostgreSQL di [Neon.tech](https://neon.tech) atau [Supabase](https://supabase.com).
2. Push repository ke GitHub.
3. Import project di [Vercel](https://vercel.com).
4. Tambahkan environment variable `DATABASE_URL` dengan connection string PostgreSQL.
5. Deploy — sistem akan otomatis membuat tabel dan seed data awal.

## 📄 Lisensi

Proyek ini dibuat untuk keperluan Kuliah Kerja Praktik (KKP) di PT. Pertamina Patra Niaga Regional Sulawesi.