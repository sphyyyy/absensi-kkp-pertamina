from app.models import User, Log, Attendance
from app.extensions import db
import openpyxl


def authenticate_user(username, password):
    """Authenticate a user by username and password.

    Returns:
        User or None.
    """
    user = User.query.filter_by(username=username, is_active=True).first()
    if user and user.check_password(password):
        return user
    return None


def create_user(username, email, password, full_name, role='mahasiswa',
                nim=None, instansi=None, phone=None):
    """Create a new user account.

    Returns:
        tuple: (user: User or None, error: str or None)
    """
    # Check existing
    if User.query.filter_by(username=username).first():
        return None, 'Username sudah digunakan.'
    if User.query.filter_by(email=email).first():
        return None, 'Email sudah digunakan.'
    if nim and User.query.filter_by(nim=nim).first():
        return None, 'NIM sudah terdaftar.'

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        nim=nim,
        instansi=instansi,
        phone=phone,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user, None


def get_all_mahasiswa():
    """Get all active mahasiswa users."""
    return User.query.filter_by(role='mahasiswa', is_active=True).order_by(
        User.full_name
    ).all()


def import_users_from_excel(file_stream, default_password='mhs123'):
    """Import mahasiswa accounts from an uploaded Excel (.xlsx) stream."""
    try:
        wb = openpyxl.load_workbook(file_stream, data_only=True)
        ws = wb.active
    except Exception as e:
        return {'success_count': 0, 'updated_count': 0, 'skipped_count': 0, 'errors': [f'Gagal membaca file Excel: {str(e)}']}

    rows = list(ws.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        return {'success_count': 0, 'updated_count': 0, 'skipped_count': 0, 'errors': ['File Excel kosong atau tidak memiliki baris data.']}

    header = [str(cell or '').strip().lower() for cell in rows[0]]

    def find_col(*keywords):
        for idx, h in enumerate(header):
            for kw in keywords:
                if kw in h:
                    return idx
        return -1

    idx_nim = find_col('nim')
    idx_name = find_col('nama', 'full_name')
    idx_email = find_col('email')
    idx_instansi = find_col('kampus', 'instansi', 'universitas')
    idx_phone = find_col('hp', 'phone', 'whatsapp', 'wa')

    if idx_name == -1 or idx_email == -1:
        return {
            'success_count': 0,
            'updated_count': 0,
            'skipped_count': 0,
            'errors': ['Header Excel wajib memiliki kolom "Nama Lengkap" dan "Email".']
        }

    success_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []

    for row_num, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue

        full_name = str(row[idx_name] or '').strip() if idx_name != -1 else ''
        email = str(row[idx_email] or '').strip().lower() if idx_email != -1 else ''
        nim = str(row[idx_nim] or '').strip() if idx_nim != -1 else None
        instansi = str(row[idx_instansi] or '').strip() if idx_instansi != -1 else None
        phone = str(row[idx_phone] or '').strip() if idx_phone != -1 else None

        if not full_name or not email:
            errors.append(f'Baris {row_num}: dilewati karena Nama atau Email kosong.')
            skipped_count += 1
            continue

        existing = None
        if nim:
            existing = User.query.filter_by(nim=nim).first()
        if not existing:
            existing = User.query.filter_by(email=email).first()

        if existing:
            existing.full_name = full_name
            existing.email = email
            if nim and not existing.nim:
                existing.nim = nim
            if instansi:
                existing.instansi = instansi
            if phone:
                existing.phone = phone
            existing.role = 'mahasiswa'
            updated_count += 1
            continue

        base_username = nim if nim else email.split('@')[0]
        base_username = ''.join(c for c in base_username if c.isalnum() or c in ('_', '-')).lower()
        if not base_username:
            base_username = f'mhs_{row_num}'

        username = base_username
        suffix = 1
        while User.query.filter_by(username=username).first():
            username = f'{base_username}{suffix}'
            suffix += 1

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role='mahasiswa',
            nim=nim,
            instansi=instansi,
            phone=phone,
            is_active=True
        )
        user.set_password(default_password)
        db.session.add(user)
        success_count += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'success_count': 0, 'updated_count': 0, 'skipped_count': 0, 'errors': [f'Gagal menyimpan ke database: {str(e)}']}

    return {
        'success_count': success_count,
        'updated_count': updated_count,
        'skipped_count': skipped_count,
        'errors': errors
    }


def reset_user_password(user_id, new_password):
    """Reset a user's password."""
    user = db.session.get(User, user_id)
    if not user:
        return False, 'User tidak ditemukan.'
    user.set_password(new_password)
    db.session.commit()
    return True, f'Password {user.username} berhasil direset.'


def toggle_user_status(user_id):
    """Toggle user active status."""
    user = db.session.get(User, user_id)
    if not user:
        return False, 'User tidak ditemukan.', None
    if user.role == 'admin':
        return False, 'Akun Admin tidak dapat dinonaktifkan.', None
    user.is_active = not user.is_active
    db.session.commit()
    status_text = 'Aktif' if user.is_active else 'Nonaktif'
    return True, f'Status {user.username} diubah menjadi {status_text}.', user.is_active


def delete_user(user_id):
    """Delete a user account and their attendance records."""
    user = db.session.get(User, user_id)
    if not user:
        return False, 'User tidak ditemukan.'
    if user.role == 'admin':
        return False, 'Akun Admin tidak dapat dihapus.'
    Attendance.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return True, f'User {user.username} berhasil dihapus.'


def update_user_profile(user_id, data):
    """Update user profile fields (full_name, email, nim, instansi, phone, username, password)."""
    user = db.session.get(User, user_id)
    if not user:
        return False, 'User tidak ditemukan.', None

    new_username = data.get('username', '').strip()
    if new_username and new_username != user.username:
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != user.id:
            return False, f'Username "{new_username}" sudah digunakan.', None
        user.username = new_username

    new_email = data.get('email', '').strip()
    if new_email and new_email != user.email:
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return False, f'Email "{new_email}" sudah digunakan.', None
        user.email = new_email

    if 'full_name' in data and data['full_name'].strip():
        user.full_name = data['full_name'].strip()
    if 'nim' in data:
        user.nim = data['nim'].strip() or None
    if 'instansi' in data:
        user.instansi = data['instansi'].strip() or None
    if 'phone' in data:
        user.phone = data['phone'].strip() or None
    if 'password' in data and data['password'].strip():
        user.set_password(data['password'].strip())

    db.session.commit()
    return True, f'Data {user.username} berhasil diperbarui.', user

