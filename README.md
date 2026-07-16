# Sistem Absensi KKP — PT. Pertamina Patra Niaga Regional Sulawesi

Sistem absensi digital berbasis web untuk mahasiswa magang (Kuliah Kerja Praktik) menggunakan Python Flask.

## Fitur Utama

- 📱 **Mobile-First** — Dioptimalkan untuk akses via smartphone
- 📍 **GPS Geofence** — Validasi lokasi otomatis dengan Haversine formula
- ⏰ **Window Waktu** — Absensi hanya bisa dilakukan pada jam yang ditentukan
- 📊 **Dashboard Dosen** — Monitoring kehadiran real-time
- 📄 **Export Laporan** — PDF & Excel report generation
- 🔒 **Keamanan** — CSRF, session, password hashing, input validation

## Tech Stack

- **Backend**: Python 3.x, Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Reports**: ReportLab (PDF), OpenPyXL (Excel)

## Quick Start

### 1. Clone & Setup

```bash
cd absensi-kkp
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Konfigurasi

Copy `.env.example` ke `.env` dan sesuaikan konfigurasi.

### 3. Inisialisasi Database

```bash
python seed.py
```

### 4. Jalankan Server

```bash
python run.py
```

Akses: http://localhost:5000

### Akun Default

| Role       | Username | Password  |
|------------|----------|-----------|
| Admin      | admin    | admin123  |
| Dosen      | dosen1   | dosen123  |
| Mahasiswa  | mhs1     | mhs123    |
| Mahasiswa  | mhs2     | mhs123    |
| Mahasiswa  | mhs3     | mhs123    |

## Struktur Folder

```
absensi-kkp/
├── app/
│   ├── auth/         # Authentication blueprint
│   ├── attendance/   # Attendance blueprint
│   ├── dashboard/    # Dashboard blueprint
│   ├── api/          # REST API blueprint
│   ├── models/       # SQLAlchemy models
│   ├── services/     # Business logic layer
│   ├── utils/        # Helpers, decorators, constants
│   ├── templates/    # Jinja2 HTML templates
│   └── static/       # CSS, JS, images
├── migrations/       # Flask-Migrate
├── uploads/          # Selfie photos
├── reports/          # Generated reports
├── run.py            # Entry point
├── seed.py           # Database seeder
└── requirements.txt
```

## License

Internal use only — PT. Pertamina Patra Niaga Regional Sulawesi.
