"""Database seeder — creates default users and settings for development."""

from app import create_app
from app.extensions import db
from app.models import User, Setting


def seed():
    """Seed the database with sample data."""
    app = create_app()

    with app.app_context():
        db.create_all()

        # Check if already seeded
        if User.query.first():
            print('Database already seeded. Skipping.')
            return

        # ── Admin ──
        admin = User(
            username='admin',
            email='admin@pertamina.com',
            full_name='Administrator',
            role='admin',
            instansi='PT. Pertamina Patra Niaga Regional Sulawesi',
        )
        admin.set_password('admin123')

        # ── Dosen Pembimbing ──
        dosen = User(
            username='dosen1',
            email='dosen@university.ac.id',
            full_name='Dr. Ahmad Fauzi, M.Kom',
            role='dosen',
            instansi='Universitas Hasanuddin',
            phone='081234567890',
        )
        dosen.set_password('dosen123')

        # ── Mahasiswa ──
        mahasiswa_data = [
            {
                'username': 'mhs1',
                'email': 'andi@student.ac.id',
                'full_name': 'Andi Pratama',
                'nim': '2021001',
                'instansi': 'Universitas Hasanuddin',
                'phone': '081111222333',
            },
            {
                'username': 'mhs2',
                'email': 'budi@student.ac.id',
                'full_name': 'Budi Santoso',
                'nim': '2021002',
                'instansi': 'Universitas Hasanuddin',
                'phone': '081444555666',
            },
            {
                'username': 'mhs3',
                'email': 'citra@student.ac.id',
                'full_name': 'Citra Dewi',
                'nim': '2021003',
                'instansi': 'Universitas Hasanuddin',
                'phone': '081777888999',
            },
        ]

        mahasiswa_users = []
        for data in mahasiswa_data:
            m = User(
                username=data['username'],
                email=data['email'],
                full_name=data['full_name'],
                nim=data['nim'],
                role='mahasiswa',
                instansi=data['instansi'],
                phone=data['phone'],
            )
            m.set_password('mhs123')
            mahasiswa_users.append(m)

        # Add all users
        db.session.add(admin)
        db.session.add(dosen)
        for m in mahasiswa_users:
            db.session.add(m)

        # ── Default Settings ──
        settings = [
            Setting(key='GEOFENCE_LAT', value='-5.1477',
                    description='Latitude kantor Pertamina'),
            Setting(key='GEOFENCE_LNG', value='119.4327',
                    description='Longitude kantor Pertamina'),
            Setting(key='GEOFENCE_RADIUS', value='100',
                    description='Radius geofence (meter)'),
            Setting(key='CHECKIN_START', value='07:00',
                    description='Jam mulai absen masuk'),
            Setting(key='CHECKIN_END', value='09:00',
                    description='Jam akhir absen masuk'),
            Setting(key='CHECKOUT_START', value='16:00',
                    description='Jam mulai absen pulang'),
            Setting(key='CHECKOUT_END', value='18:00',
                    description='Jam akhir absen pulang'),
        ]

        for s in settings:
            db.session.add(s)

        db.session.commit()

        print('[OK] Database seeded successfully!')
        print()
        print('Akun yang dibuat:')
        print('-' * 40)
        print('  Admin    : admin / admin123')
        print('  Dosen    : dosen1 / dosen123')
        print('  Mahasiswa: mhs1 / mhs123')
        print('  Mahasiswa: mhs2 / mhs123')
        print('  Mahasiswa: mhs3 / mhs123')
        print('-' * 40)


if __name__ == '__main__':
    seed()
