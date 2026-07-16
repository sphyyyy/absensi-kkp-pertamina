"""
==========================================================================
   COMPREHENSIVE MAINTENANCE TEST - Sistem Absensi KKP Pertamina
   Menguji seluruh fitur utama secara otomatis (Single Client Session)
==========================================================================
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Attendance, Setting, Log

TEST_RESULTS = []
PASS_COUNT = 0
FAIL_COUNT = 0


def log_result(test_name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    status = "PASS" if passed else "FAIL"
    icon = "[V]" if passed else "[X]"
    if passed:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    TEST_RESULTS.append((test_name, status, detail))
    print(f"  {icon} {status}  {test_name}" + (f" -- {detail}" if detail else ""))


def run_all_tests():
    global PASS_COUNT, FAIL_COUNT
    app = create_app('testing')

    print("")
    print("=" * 70)
    print("   COMPREHENSIVE MAINTENANCE TEST - Sistem Absensi KKP")
    print("=" * 70)

    with app.app_context():
        db.create_all()

        # Prepare: admin account
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@pertamina.com',
                         full_name='Administrator', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        # Prepare: mahasiswa account
        mhs = User.query.filter_by(username='test_mhs').first()
        if not mhs:
            mhs = User(username='test_mhs', email='test_mhs@tes.com',
                        full_name='Mahasiswa Tes', role='mahasiswa', nim='9999001')
            mhs.set_password('mhs123')
            db.session.add(mhs)
            db.session.commit()

        c = app.test_client()

        # ====================================================
        # MODUL 1: AUTENTIKASI
        # ====================================================
        print("\n-- MODUL 1: AUTENTIKASI --")

        # 1.1 Halaman Login GET
        res = c.get('/auth/login')
        log_result("1.1 Halaman Login Terbuka (GET /auth/login)",
            res.status_code == 200 and b'login' in res.data.lower(),
            f"Status: {res.status_code}")

        # 1.2 Login Gagal (username salah)
        res = c.post('/auth/login', data={'username': 'xyz_invalid', 'password': 'salah'}, follow_redirects=True)
        log_result("1.2 Login Gagal (Username Salah)",
            res.status_code == 200 and b'login' in res.data.lower(),
            f"Status: {res.status_code}")

        # 1.3 Login Gagal (password salah)
        res = c.post('/auth/login', data={'username': 'admin', 'password': 'salah'}, follow_redirects=True)
        log_result("1.3 Login Gagal (Password Salah)",
            res.status_code == 200 and b'login' in res.data.lower(),
            f"Status: {res.status_code}")

        # 1.4 Login Berhasil (Admin)
        res = c.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        log_result("1.4 Login Berhasil (Admin -> Dashboard)",
            res.status_code == 200 and b'admin' in res.data.lower(),
            f"Status: {res.status_code}")

        # 1.5 Logout
        res = c.get('/auth/logout', follow_redirects=True)
        log_result("1.5 Logout Berhasil (Redirect ke Login)",
            res.status_code == 200 and b'login' in res.data.lower(),
            f"Status: {res.status_code}")

        # 1.6 Login Berhasil (Mahasiswa)
        res = c.post('/auth/login', data={'username': 'test_mhs', 'password': 'mhs123'}, follow_redirects=True)
        log_result("1.6 Login Berhasil (Mahasiswa -> Dashboard)",
            res.status_code == 200, f"Status: {res.status_code}")

        # 1.7 RBAC - Mahasiswa Ditolak Akses Admin
        res = c.get('/dashboard/admin', follow_redirects=True)
        log_result("1.7 RBAC - Mahasiswa Ditolak Akses Admin (403)",
            res.status_code == 403 or b'403' in res.data,
            f"Status: {res.status_code}")

        # Logout mahasiswa
        c.get('/auth/logout')

        # 1.8 Akses tanpa login
        res = c.get('/dashboard/mahasiswa', follow_redirects=False)
        log_result("1.8 Akses Dashboard Tanpa Login (Redirect)",
            res.status_code in (301, 302), f"Status: {res.status_code}")

        # ====================================================
        # MODUL 2: ADMIN - KELOLA MAHASISWA (CRUD)
        # ====================================================
        print("\n-- MODUL 2: ADMIN - KELOLA MAHASISWA (CRUD) --")

        # Login as admin untuk seluruh MODUL 2
        c.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

        # 2.1 Tambah Mahasiswa Baru
        res = c.post('/api/admin/users/add', json={
            'username': 'test_tambah_mhs', 'full_name': 'Tambah Tes Mahasiswa',
            'email': 'tambah.mhs@test.com', 'role': 'mahasiswa', 'password': 'mhs123',
            'nim': '8888001', 'instansi': 'Univ Tes', 'phone': '081000000001'
        })
        data = res.get_json() or {}
        log_result("2.1 Tambah Mahasiswa Baru",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', data.get('error', ''))}")

        # 2.2 Tambah Dosen Baru
        res = c.post('/api/admin/users/add', json={
            'username': 'test_tambah_dosen', 'full_name': 'Dr. Dosen Tes',
            'email': 'tambah.dosen@test.com', 'role': 'dosen',
            'password': 'dosen123', 'instansi': 'Universitas Tes'
        })
        data = res.get_json() or {}
        log_result("2.2 Tambah Dosen Baru",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', data.get('error', ''))}")

        # 2.3 Tambah Duplikat (ditolak)
        res = c.post('/api/admin/users/add', json={
            'username': 'test_tambah_mhs', 'full_name': 'Duplikat',
            'email': 'tambah.mhs@test.com', 'role': 'mahasiswa', 'password': 'mhs123'
        })
        data = res.get_json() or {}
        log_result("2.3 Tolak Tambah Username Duplikat (400)",
            res.status_code == 400 and data.get('error') is not None,
            f"Status: {res.status_code}, Error: {data.get('error', '')}")

        # 2.4 Tambah tanpa field wajib (ditolak)
        res = c.post('/api/admin/users/add', json={
            'username': '', 'full_name': '', 'email': '', 'password': ''
        })
        log_result("2.4 Tolak Tambah Tanpa Field Wajib (400)",
            res.status_code == 400, f"Status: {res.status_code}")

        # 2.5 Update Profil Mahasiswa
        user = User.query.filter_by(username='test_tambah_mhs').first()
        res = c.post(f'/api/admin/users/{user.id}/update', json={
            'full_name': 'Nama Sudah Diupdate', 'phone': '089999999999'
        })
        data = res.get_json() or {}
        log_result("2.5 Update Profil Mahasiswa",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Nama: {data.get('user', {}).get('full_name', '')}")

        # 2.6 Reset Password
        res = c.post(f'/api/admin/users/{user.id}/reset-password', json={'password': 'pw_baru_123'})
        data = res.get_json() or {}
        log_result("2.6 Reset Password Mahasiswa",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', '')}")
        user_check = User.query.filter_by(username='test_tambah_mhs').first()
        pw_ok = user_check.check_password('pw_baru_123') if user_check else False
        log_result("2.6b Verifikasi Password Baru", pw_ok, f"check_password: {pw_ok}")

        # 2.7 Toggle Status
        res = c.post(f'/api/admin/users/{user.id}/toggle-status')
        data = res.get_json() or {}
        log_result("2.7 Toggle Status Mahasiswa",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, is_active: {data.get('is_active')}")

        # 2.8 Hapus Dosen
        dosen = User.query.filter_by(username='test_tambah_dosen').first()
        res = c.delete(f'/api/admin/users/{dosen.id}/delete')
        data = res.get_json() or {}
        log_result("2.8 Hapus Dosen (DELETE)",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', '')}")
        deleted = User.query.filter_by(username='test_tambah_dosen').first()
        log_result("2.8b Verifikasi Dosen Terhapus", deleted is None, f"query: {deleted}")

        # 2.9 Hapus Mahasiswa
        user = User.query.filter_by(username='test_tambah_mhs').first()
        res = c.delete(f'/api/admin/users/{user.id}/delete')
        data = res.get_json() or {}
        log_result("2.9 Hapus Mahasiswa (DELETE)",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', '')}")

        # 2.10 Hapus User Tidak Ada (404)
        res = c.delete('/api/admin/users/999999/delete')
        log_result("2.10 Hapus User Tidak Ada (404)",
            res.status_code == 404, f"Status: {res.status_code}")

        # ====================================================
        # MODUL 3: ADMIN - IMPORT EXCEL
        # ====================================================
        print("\n-- MODUL 3: ADMIN - IMPORT EXCEL --")

        # 3.1 Download Template Excel
        res = c.get('/api/admin/users/template-excel')
        log_result("3.1 Download Template Excel",
            res.status_code == 200 and 'spreadsheet' in (res.content_type or ''),
            f"Status: {res.status_code}, Type: {res.content_type}")

        # 3.2 Import Excel Mahasiswa
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['NIM', 'Nama Lengkap', 'Email', 'Kampus/Instansi', 'No HP'])
        ws.append(['7777001', 'Excel Mhs Satu', 'excel1@test.com', 'Univ Excel', '08100001'])
        ws.append(['7777002', 'Excel Mhs Dua', 'excel2@test.com', 'Univ Excel', '08100002'])
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        res = c.post('/api/admin/users/import-excel',
            data={'file': (stream, 'test_import.xlsx')},
            content_type='multipart/form-data')
        data = res.get_json() or {}
        log_result("3.2 Import Excel Mahasiswa (2 akun baru)",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', data.get('error', ''))}")
        u1 = User.query.filter_by(nim='7777001').first()
        u2 = User.query.filter_by(nim='7777002').first()
        log_result("3.2b Verifikasi Akun Excel Ter-import",
            u1 is not None and u2 is not None,
            f"mhs1: {u1 is not None}, mhs2: {u2 is not None}")

        # 3.3 Import File Non-Excel (ditolak)
        fake_file = io.BytesIO(b"ini bukan excel")
        res = c.post('/api/admin/users/import-excel',
            data={'file': (fake_file, 'data.txt')},
            content_type='multipart/form-data')
        log_result("3.3 Tolak Import File Non-Excel (.txt -> 400)",
            res.status_code == 400, f"Status: {res.status_code}")

        # ====================================================
        # MODUL 4: DASHBOARD & HALAMAN
        # ====================================================
        print("\n-- MODUL 4: DASHBOARD & HALAMAN --")

        # 4.1 Dashboard Admin (masih login admin)
        res = c.get('/dashboard/admin')
        log_result("4.1 Dashboard Admin Terbuka",
            res.status_code == 200, f"Status: {res.status_code}")

        # Logout, login sebagai mahasiswa
        c.get('/auth/logout')
        c.post('/auth/login', data={'username': 'test_mhs', 'password': 'mhs123'}, follow_redirects=True)

        # 4.2 Dashboard Mahasiswa
        res = c.get('/dashboard/mahasiswa')
        log_result("4.2 Dashboard Mahasiswa Terbuka",
            res.status_code == 200, f"Status: {res.status_code}")

        # 4.3 Riwayat Absensi
        res = c.get('/dashboard/mahasiswa/riwayat')
        log_result("4.3 Halaman Riwayat Absensi Terbuka",
            res.status_code == 200, f"Status: {res.status_code}")

        c.get('/auth/logout')

        # 4.4 Error 404
        res = c.get('/halaman-tidak-ada-xyz')
        log_result("4.4 Halaman Error 404", res.status_code == 404, f"Status: {res.status_code}")

        # 4.5 Root redirect
        res = c.get('/', follow_redirects=False)
        log_result("4.5 Root (/) Redirect", res.status_code in (301, 302), f"Status: {res.status_code}")

        # ====================================================
        # MODUL 5: STATIC FILES & ASSETS
        # ====================================================
        print("\n-- MODUL 5: STATIC FILES --")
        for path, label in [
            ('/static/css/style.css', '5.1 CSS style.css'),
            ('/static/js/app.js', '5.2 JavaScript app.js'),
            ('/static/logo_pertamina.png', '5.3 Logo Pertamina'),
            ('/static/js/geolocation.js', '5.4 Geolocation JS'),
            ('/static/js/dashboard.js', '5.5 Dashboard JS'),
        ]:
            res = c.get(path)
            log_result(f"{label} Tersajikan",
                res.status_code == 200,
                f"Status: {res.status_code}, Size: {len(res.data)} bytes")

        # ====================================================
        # MODUL 6: ABSENSI
        # ====================================================
        print("\n-- MODUL 6: ABSENSI --")

        c.post('/auth/login', data={'username': 'test_mhs', 'password': 'mhs123'}, follow_redirects=True)

        res = c.get('/attendance/status')
        data = res.get_json() or {}
        log_result("6.1 Cek Status Absensi (GET /attendance/status)",
            res.status_code == 200 and 'checked_in' in data, f"Status: {res.status_code}")

        res = c.post('/attendance/check-in', data='', content_type='application/json')
        log_result("6.2 Check-in Tanpa Data (400)", res.status_code == 400, f"Status: {res.status_code}")

        res = c.post('/attendance/check-in',
            json={'latitude': -5.1477, 'longitude': 119.4327, 'accuracy': 10})
        data = res.get_json() or {}
        log_result("6.3 Check-in dengan GPS (Response Valid)",
            res.status_code in (200, 400) and data.get('message') is not None,
            f"Status: {res.status_code}, Msg: {data.get('message', '')}")

        res = c.post('/attendance/check-out', data='', content_type='application/json')
        log_result("6.4 Check-out Tanpa Data (400)", res.status_code == 400, f"Status: {res.status_code}")

        c.get('/auth/logout')

        # ====================================================
        # MODUL 7: PENGATURAN GEOFENCE
        # ====================================================
        print("\n-- MODUL 7: PENGATURAN GEOFENCE --")

        c.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

        res = c.post('/api/admin/settings/update', json={
            'GEOFENCE_LAT': '-5.1500', 'GEOFENCE_LNG': '119.4400', 'GEOFENCE_RADIUS': '150'
        })
        data = res.get_json() or {}
        log_result("7.1 Update Geofence Settings",
            res.status_code == 200 and data.get('success') is True,
            f"Status: {res.status_code}, Resp: {data.get('message', '')}")

        res = c.post('/api/admin/settings/update', json={})
        log_result("7.2 Update Settings Tanpa Data (400)",
            res.status_code == 400, f"Status: {res.status_code}")

        res = c.post('/api/admin/settings/update', json={
            'CHECKIN_START': '07:30', 'CHECKIN_END': '09:30',
            'CHECKOUT_START': '16:30', 'CHECKOUT_END': '18:30'
        })
        data = res.get_json() or {}
        log_result("7.3 Update Waktu Absensi",
            res.status_code == 200 and data.get('success') is True, f"Status: {res.status_code}")

        c.get('/auth/logout')

        # ====================================================
        # MODUL 8: AUDIT LOG
        # ====================================================
        print("\n-- MODUL 8: AUDIT LOG --")

        recent_logs = Log.query.order_by(Log.created_at.desc()).limit(10).all()
        log_result("8.1 Audit Log Tercatat di Database",
            len(recent_logs) > 0, f"Jumlah log: {len(recent_logs)}")
        if recent_logs:
            log_result("8.2 Audit Log Memiliki Detail Aksi",
                recent_logs[0].action is not None and recent_logs[0].detail is not None,
                f"Action: {recent_logs[0].action}")

        # ====================================================
        # MODUL 9: MODEL & DATABASE INTEGRITY
        # ====================================================
        print("\n-- MODUL 9: MODEL & DATABASE --")

        u = User(username='test_hash', email='h@t.com', full_name='Hash', role='mahasiswa')
        u.set_password('rahasia123')
        log_result("9.1 Password Hashing",
            u.check_password('rahasia123') and not u.check_password('salah') and u.password_hash != 'rahasia123',
            "Hash != plaintext, verifikasi benar")

        Setting.set('TEST_K', 'tv123')
        val = Setting.get('TEST_K')
        log_result("9.2 Setting Model (Set & Get)", val == 'tv123', f"Set='tv123', Get='{val}'")
        Setting.query.filter_by(key='TEST_K').delete()
        db.session.commit()

        ac = User.query.filter_by(role='admin').count()
        mc = User.query.filter_by(role='mahasiswa').count()
        log_result("9.3 User Roles Terdeteksi", ac > 0 and mc > 0, f"Admin: {ac}, Mahasiswa: {mc}")

        from sqlalchemy import inspect
        tables = inspect(db.engine).get_table_names()
        required = ['users', 'attendance', 'settings', 'logs']
        missing = [t for t in required if t not in tables]
        log_result("9.4 Tabel Database Lengkap", len(missing) == 0,
            f"Found: {tables}, Missing: {missing}")

        # ====================================================
        # CLEANUP
        # ====================================================
        print("\n-- CLEANUP --")
        cleanup = User.query.filter(
            (User.username.like('test_%')) | (User.nim.in_(['7777001', '7777002', '8888001']))
        ).all()
        for u in cleanup:
            db.session.delete(u)
        db.session.commit()
        print(f"  [*] Membersihkan {len(cleanup)} akun tes dari database.")

    # ====================================================
    # LAPORAN AKHIR
    # ====================================================
    print("")
    print("=" * 110)
    print("   LAPORAN HASIL COMPREHENSIVE MAINTENANCE TEST")
    print("=" * 110)
    print(f"{'No.':<5} {'Status':<8} {'Nama Tes':<62} {'Detail'}")
    print("-" * 110)
    for i, (name, status, detail) in enumerate(TEST_RESULTS, 1):
        icon = "[V]" if status == "PASS" else "[X]"
        ds = (detail[:42] + '...') if len(detail) > 44 else detail
        print(f"{i:<5} {icon} {status:<5} {name:<62} {ds}")
    print("-" * 110)
    total = PASS_COUNT + FAIL_COUNT
    pct = (PASS_COUNT / total * 100) if total > 0 else 0
    print(f"\n   TOTAL: {total} tes  |  PASS: {PASS_COUNT}  |  FAIL: {FAIL_COUNT}  |  SKOR: {pct:.1f}%")
    if FAIL_COUNT == 0:
        print("\n   SEMUA TES LULUS 100%! SISTEM ABSENSI KKP SEHAT SEMPURNA!")
    else:
        print(f"\n   PERHATIAN: Terdapat {FAIL_COUNT} tes gagal yang perlu diperbaiki.")
    print("=" * 110 + "\n")
    return FAIL_COUNT == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
