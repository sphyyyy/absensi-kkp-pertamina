"""
Automated test script for Admin Portal, Bulk Excel Import, and User Management.
Run with: python test_admin_portal.py
"""
import io
import os
import sys
import openpyxl

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Setting, Log


def run_tests():
    print("=" * 60)
    print("STARTING ADMIN PORTAL & EXCEL IMPORT VERIFICATION TESTS")
    print("=" * 60)

    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create test admin if not exists
            admin = User.query.filter_by(username='admin_test').first()
            if not admin:
                admin = User(
                    username='admin_test',
                    email='admin_test@pertamina.com',
                    full_name='Admin Test Pertamina',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)

            # Create test mahasiswa if not exists
            mhs = User.query.filter_by(username='mhs_test').first()
            if not mhs:
                mhs = User(
                    username='mhs_test',
                    email='mhs_test@example.com',
                    full_name='Mahasiswa Test',
                    role='mahasiswa',
                    nim='2026999',
                    is_active=True
                )
                mhs.set_password('mhs123')
                db.session.add(mhs)

            # Create test dosen if not exists
            dosen = User.query.filter_by(username='dosen_test').first()
            if not dosen:
                dosen = User(
                    username='dosen_test',
                    email='dosen_test@example.com',
                    full_name='Dosen Test',
                    role='dosen',
                    is_active=True
                )
                dosen.set_password('dosen123')
                db.session.add(dosen)

            db.session.commit()
            admin_id = admin.id
            mhs_id = mhs.id
            dosen_id = dosen.id

        # 1. Test Admin Access vs Mahasiswa Access on /dashboard/admin
        print("\n[TEST 1] Verifying RBAC on /dashboard/admin...")
        # Login as mahasiswa
        client.post('/auth/login', data={'username': 'mhs_test', 'password': 'mhs123'}, follow_redirects=True)
        res_mhs = client.get('/dashboard/admin')
        assert res_mhs.status_code == 403, f"Expected 403 for mhs on /dashboard/admin, got {res_mhs.status_code}"
        client.get('/auth/logout', follow_redirects=True)
        print(" -> Mahasiswa correctly forbidden (403) on Admin Portal!")

        # Login as admin
        client.post('/auth/login', data={'username': 'admin_test', 'password': 'admin123'}, follow_redirects=True)
        res_admin = client.get('/dashboard/admin')
        assert res_admin.status_code == 200, f"Expected 200 for admin on /dashboard/admin, got {res_admin.status_code}"
        assert b"Bulk Import Mahasiswa via Excel" in res_admin.data
        print(" -> Admin successfully accessed /dashboard/admin (200 OK)!")

        # 2. Test Download Template Excel
        print("\n[TEST 2] Verifying Download Template Excel...")
        res_tpl = client.get('/api/admin/users/template-excel')
        assert res_tpl.status_code == 200, f"Expected 200 on get_template_excel, got {res_tpl.status_code}"
        assert 'template_mahasiswa.xlsx' in res_tpl.headers.get('Content-Disposition', '')
        print(" -> Template Excel successfully generated and downloaded!")

        # 3. Test Bulk Excel Import
        print("\n[TEST 3] Verifying Bulk Excel Import...")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['NIM', 'Nama Lengkap', 'Email', 'Kampus/Instansi', 'No HP'])
        ws.append(['2026001', 'Anisa Rahma', 'anisa@univ.ac.id', 'Universitas Hasanuddin', '08111111'])
        ws.append(['2026002', 'Farhan Akbar', 'farhan@univ.ac.id', 'Universitas Negeri Makassar', '08222222'])
        ws.append(['2026003', 'Citra Dewi', 'citra@univ.ac.id', 'Universitas Sam Ratulangi', '08333333'])

        excel_stream = io.BytesIO()
        wb.save(excel_stream)
        excel_stream.seek(0)

        data = {'file': (excel_stream, 'import_mahasiswa.xlsx')}
        res_imp = client.post('/api/admin/users/import-excel', data=data, content_type='multipart/form-data')
        assert res_imp.status_code == 200, f"Expected 200 on import-excel, got {res_imp.status_code} ({res_imp.data})"
        imp_json = res_imp.get_json()
        assert imp_json['data']['success_count'] == 3, f"Expected 3 imported, got {imp_json['data']['success_count']}"
        print(f" -> Bulk Excel Import successful! Message: {imp_json['message']}")

        # Verify in database
        with app.app_context():
            u1 = User.query.filter_by(nim='2026001').first()
            assert u1 and u1.full_name == 'Anisa Rahma' and u1.check_password('mhs123')
            print(" -> Created user Anisa Rahma verified in DB with default password mhs123!")

        # 4. Test Reset Password
        print("\n[TEST 4] Verifying Reset Password...")
        with app.app_context():
            target_id = User.query.filter_by(nim='2026001').first().id

        res_reset = client.post(f'/api/admin/users/{target_id}/reset-password', json={'password': 'newpassword123'})
        assert res_reset.status_code == 200
        with app.app_context():
            u1_check = db.session.get(User, target_id)
            assert u1_check.check_password('newpassword123')
        print(" -> Password reset verified via API successfully!")

        # 5. Test Update Settings
        print("\n[TEST 5] Verifying System Settings Update via API...")
        res_set = client.post('/api/admin/settings/update', json={
            'GEOFENCE_LAT': '-5.1500',
            'GEOFENCE_LNG': '119.4300',
            'GEOFENCE_RADIUS': '150'
        })
        assert res_set.status_code == 200
        with app.app_context():
            assert Setting.get('GEOFENCE_RADIUS') == '150'
            assert Setting.get('GEOFENCE_LAT') == '-5.1500'
        print(" -> Runtime settings update verified in database!")

        # 6. Test Update User Profile
        print("\n[TEST 6] Verifying User Profile Update via API...")
        res_upd = client.post(f'/api/admin/users/{target_id}/update', json={
            'full_name': 'Anisa Rahma Diperbarui',
            'email': 'anisa_new@univ.ac.id',
            'nim': '2026001',
            'instansi': 'Universitas Hasanuddin Baru',
            'phone': '0899999999'
        })
        assert res_upd.status_code == 200, f"Expected 200 on update user, got {res_upd.status_code} ({res_upd.data})"
        with app.app_context():
            u_check = db.session.get(User, target_id)
            assert u_check.full_name == 'Anisa Rahma Diperbarui'
            assert u_check.phone == '0899999999'
        print(" -> User profile update verified in database successfully!")

        # 7. Test Dosen Dashboard access restriction (Only dosen allowed, Admin & Mahasiswa forbidden)
        print("\n[TEST 7] Verifying Dosen Dashboard strictly restricted to Dosen role...")
        client.get('/auth/logout', follow_redirects=True)
        # Login as Admin -> should get 403 on /dashboard/dosen
        client.post('/auth/login', data={'username': 'admin_test', 'password': 'admin123'}, follow_redirects=True)
        res_admin_dosen = client.get('/dashboard/dosen')
        assert res_admin_dosen.status_code == 403, f"Expected 403 for Admin on /dashboard/dosen, got {res_admin_dosen.status_code}"
        
        client.get('/auth/logout', follow_redirects=True)
        # Login as Mahasiswa -> should get 403 on /dashboard/dosen
        client.post('/auth/login', data={'username': 'mhs_test', 'password': 'mhs123'}, follow_redirects=True)
        res_mhs_dosen = client.get('/dashboard/dosen')
        assert res_mhs_dosen.status_code == 403, f"Expected 403 for Mahasiswa on /dashboard/dosen, got {res_mhs_dosen.status_code}"

        client.get('/auth/logout', follow_redirects=True)
        # Login as Dosen -> should get 200 OK on /dashboard/dosen
        client.post('/auth/login', data={'username': 'dosen_test', 'password': 'dosen123'}, follow_redirects=True)
        res_dosen_ok = client.get('/dashboard/dosen')
        assert res_dosen_ok.status_code == 200, f"Expected 200 for Dosen on /dashboard/dosen, got {res_dosen_ok.status_code}"
        print(" -> Dosen Dashboard isolation verified: Admin and Mahasiswa get 403, Dosen gets 200 OK!")

        print("\n" + "=" * 60)
        print("ALL 7 ADMIN PORTAL, DOSEN ISOLATION & EXCEL IMPORT TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)


if __name__ == '__main__':
    run_tests()
