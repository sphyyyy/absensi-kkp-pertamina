# Sistem Absensi KKP — PT. Pertamina Patra Niaga Regional Sulawesi

Sistem absensi digital berbasis web untuk mahasiswa magang (Kuliah Kerja Praktik) menggunakan Python Flask, rancangan UI modern glassmorphism, serta dukungan deployment penuh ke serverless Vercel dan PostgreSQL Cloud.

## 🌟 Fitur Utama

- 📱 **Mobile-First & Modern UI** — Desain berantarmuka modern (Glassmorphism), Hero Carousel pada halaman login, dan tampilan yang sangat responsif baik di smartphone maupun laptop.
- 📍 **GPS Geofence Validation** — Pengecekan koordinat real-time dengan Haversine Formula untuk memastikan mahasiswa hanya dapat melakukan absensi dalam radius koordinat kantor yang ditentukan.
- ⏰ **Dynamic Time Windows (*Runtime Configuration*)** — Jam absensi masuk & pulang serta batas toleransi keterlambatan yang dapat diatur langsung oleh Admin via Dashboard tanpa perlu *restart server* (*anti-reset* pada Vercel).
- 👥 **Role-Based Access Control (RBAC)** — Sistem multi-peran dengan hak akses khusus untuk **Admin**, **Dosen Pembimbing**, dan **Mahasiswa Magang**.
- 📊 **Dashboard Manajemen Lengkap** —
  - **Admin**: CRUD data mahasiswa & dosen, impor mahasiswa massal via Excel (`.xlsx`), unduh template Excel, kelola jam/geofence, serta pantau *Audit Logs* keamanan sistem.
  - **Dosen**: Pantau status kehadiran mahasiswa bimbingan secara real-time.
  - **Mahasiswa**: Absen masuk/pulang berbasis GPS, riwayat absensi harian, dan statistik kehadiran.
- 📄 **Export Laporan Profesional** — Ekspor riwayat dan rekap absensi ke format **Excel (.xlsx)** (OpenPyXL) dan **PDF** (ReportLab).
- ☁️ **Cloud & Serverless Ready** — Mendukung deployment instan ke **Vercel (`vercel.app`)** dengan fitur auto-seed database, integrasi **PostgreSQL Cloud** (Neon.tech / Supabase), serta tunneling lokal (`run_tunnel.py` / Ngrok).
- 🔒 **Keamanan & Audit Sistem** — Proteksi CSRF Token di setiap formulir/AJAX, *Password Hashing* (Werkzeug), proteksi sesi pengguna, dan pencatatan riwayat aktivitas (*Audit Logs*).

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, Flask, SQLAlchemy ORM, Flask-Login, Flask-WTF / CSRFProtect
- **Frontend**: HTML5, CSS3 Custom Tokens, Bootstrap 5, Vanilla JavaScript, SweetAlert2 / Native Modals
- **Database**: SQLite (Development / Ngrok Tunnel) & PostgreSQL Cloud (Production Vercel)
- **Reports & Files**: ReportLab (PDF), OpenPyXL (Excel Import/Export)

## 🚀 Quick Start (Menjalankan di Laptop)

### 1. Clone & Persiapkan Environment

```bash
git clone https://github.com/sphyyyy/absensi-kkp-pertamina.git
cd absensi-kkp-pertamina
python -m venv venv
venv\Scripts\activate     # Windows PowerShell / CMD
# source venv/bin/activate  # Linux / Mac
pip install -r requirements.txt
```

### 2. Konfigurasi Lingkungan (.env)

Salin file `.env.example` menjadi `.env` dan sesuaikan parameter berikut (opsional untuk pengembangan lokal):
```env
SECRET_KEY=rahasia-negara-kkp-2026
GEOFENCE_LATITUDE=-5.147665
GEOFENCE_LONGITUDE=119.432732
GEOFENCE_RADIUS_METERS=500
CHECKIN_START=07:00
CHECKIN_END=23:00
CHECKOUT_START=16:00
CHECKOUT_END=23:59
```

### 3. Inisialisasi & Seeding Database

Jalankan skrip *seeder* untuk membuat struktur tabel dan mengisi akun default beserta data awal:
```bash
python seed.py
```

### 4. Jalankan Server Web

#### Pilihan A: Menjalankan Server Lokal Biasa
```bash
python run.py
```
> Akses melalui browser di: `http://localhost:5000`

#### Pilihan B: Menjalankan dengan Tunnel Ngrok (Bisa Diakses via HP dari Mana Saja)
```bash
python run_tunnel.py
```
> Skrip akan otomatis membuka port 5000 dan menampilkan URL HTTPS publik (`https://...ngrok-free.app`) yang bisa langsung dibuka di browser smartphone Anda.

---

## 🔑 Akun Default (Siap Pakai)

Berikut adalah daftar akun yang otomatis dibuat setelah menjalankan `seed.py` atau saat *cold boot* di Vercel:

| Role | Username / NIM | Password | Keterangan |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Akses penuh manajemen sistem, geofence, impor Excel, & log audit |
| **Dosen** | `dosen1` / `19850101...` | `dosen123` | Dosen pembimbing magang (`Dr. Ahmad Fauzi, M.Kom`) |
| **Mahasiswa** | `2361008` | `mhs123` | Akun utama mahasiswa KKP (`sphyyy`) |
| **Mahasiswa** | `mhs1` (`2021001`) | `mhs123` | Akun mahasiswa tes (`Andi Pratama`) |
| **Mahasiswa** | `mhs2` (`2021002`) | `mhs123` | Akun mahasiswa tes (`Budi Santoso`) |
| **Mahasiswa** | `mhs3` (`2021003`) | `mhs123` | Akun mahasiswa tes (`Citra Dewi`) |

---

## ☁️ Panduan Deployment ke Vercel & PostgreSQL Cloud

Aplikasi ini dirancang *100% Serverless Ready*. Jika Anda ingin meng-online-kan aplikasi secara gratis selamanya di Vercel dengan penyimpanan data permanen di PostgreSQL Cloud (Neon.tech / Supabase):

1. **Buat Database PostgreSQL di Neon.tech / Supabase**:
   * Buat project baru dan salin *Connection String* Anda (`postgresql://user:password@host.region.aws.neon.tech/dbname?sslmode=require`).
2. **Push Kode ke GitHub**:
   * Cukup klik ganda file **`Upload_Ke_GitHub.bat`** di folder proyek Anda atau jalankan `git push origin main --force`.
3. **Impor ke Vercel**:
   * Masuk ke dashboard [Vercel.com](https://vercel.com), klik **Add New Project**, dan pilih repository GitHub Anda.
   * Di menu **Environment Variables**, tambahkan variabel:
     * `DATABASE_URL` = *(Paste connection string PostgreSQL Anda)*
   * Klik **Deploy**.
4. **Selesai!** Saat pertama kali dibuka, sistem akan otomatis menjalankan *auto-seed hook* di `api/index.py` untuk membangun seluruh tabel database di PostgreSQL secara langsung.

---

## 📁 Struktur Folder Proyek

```
absensi-kkp/
├── api/
│   └── index.py              # Serverless entry point untuk Vercel (dengan Auto-Seed Hook)
├── app/
│   ├── api/                  # Blueprint REST API (Pengaturan, Status, Laporan AJAX)
│   ├── attendance/           # Blueprint & logika proses Check-In/Check-Out GPS
│   ├── auth/                 # Blueprint Login, Logout, dan manajemen Sesi
│   ├── dashboard/            # Blueprint tampilan halaman Admin, Dosen, dan Mahasiswa
│   ├── models/               # Model database SQLAlchemy (User, Attendance, Setting, AuditLog)
│   ├── services/             # Core Business Logic (Validasi Geofence, Pengecekan Waktu)
│   ├── static/               # Aset statis (CSS glassmorphism, JS interaktif, Logo Pertamina)
│   ├── templates/            # Template HTML Jinja2 (Login Hero Carousel, Dashboard Admin, dll.)
│   └── utils/                # Fungsi bantuan (Cleaning Time, RBAC Decorators, CSRF helpers)
├── reports/                  # Direktori hasil ekspor laporan PDF & Excel
├── run.py                    # Entry point server web lokal Flask
├── run_tunnel.py             # Entry point server dengan integrasi Ngrok Tunnel HTTPS
├── seed.py                   # Skrip pengisi data awal database (Seeder)
├── test_maintenance.py       # Comprehensive Test Suite (47 skenario pengujian otomatis 100% lulus)
├── vercel.json               # Konfigurasi routing & static build untuk Vercel Serverless
├── Upload_Ke_GitHub.bat      # Skrip otomatisasi git push ke repository GitHub
└── requirements.txt          # Daftar dependensi perpustakaan Python
```

---

## 🧪 Pengujian Otomatis (*Automated Testing Suite*)

Proyek ini dilengkapi dengan skrip pengujian pemeliharaan menyeluruh (`test_maintenance.py`) yang menguji **47 skenario** (Login RBAC, CRUD Mahasiswa/Dosen, Impor/Ekspor Excel, Validasi Geofence & Waktu, Audit Log, dan Keamanan Password).

Untuk menjalankan pengujian:
```bash
python test_maintenance.py
```
> *Hasil yang diharapkan*: `TOTAL: 47 tes | PASS: 47 | FAIL: 0 | SKOR: 100.0%`

---

## 📜 Lisensi & Atribusi

Dibuat sebagai Proyek Kuliah Kerja Praktik (KKP) oleh **sphyyy (`2361008`)**  
**PT. Pertamina Patra Niaga Regional Sulawesi**  
*Hak Cipta Dilindungi — Penggunaan Internal.*
