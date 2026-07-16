import io
import openpyxl
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Attendance, User, Setting, Log
from app.services.report_service import generate_pdf_report, generate_excel_report
from app.services.auth_service import (
    import_users_from_excel, create_user, reset_user_password,
    toggle_user_status, delete_user, update_user_profile
)
from app.utils.decorators import dosen_required, admin_required
from app.utils.helpers import format_time, format_date

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/attendance', methods=['GET'])
@login_required
@dosen_required
def get_attendance():
    """Get filtered attendance data as JSON."""
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    search = request.args.get('search', '').strip()

    query = (
        Attendance.query
        .join(User)
        .filter(Attendance.is_valid == True)  # noqa: E712
    )

    if start:
        query = query.filter(Attendance.attendance_date >= start)
    if end:
        query = query.filter(Attendance.attendance_date <= end)
    if search:
        query = query.filter(
            User.full_name.ilike(f'%{search}%') |
            User.nim.ilike(f'%{search}%')
        )

    records = query.order_by(
        Attendance.attendance_date.desc(), User.full_name
    ).limit(500).all()

    data = []
    for r in records:
        data.append({
            'id': r.id,
            'nama': r.user.full_name,
            'nim': r.user.nim or '-',
            'tanggal': format_date(r.attendance_date),
            'jam_masuk': format_time(r.check_in_time),
            'jam_pulang': format_time(r.check_out_time),
            'status': r.status.capitalize(),
        })

    return jsonify({'data': data, 'total': len(data)})


@api_bp.route('/export/pdf', methods=['GET'])
@login_required
@dosen_required
def export_pdf():
    """Generate and download a PDF attendance report."""
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if not start or not end:
        return jsonify({'error': 'Parameter start_date dan end_date wajib diisi.'}), 400

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    filepath = generate_pdf_report(start_date, end_date)
    return send_file(filepath, as_attachment=True)


@api_bp.route('/export/excel', methods=['GET'])
@login_required
@dosen_required
def export_excel():
    """Generate and download an Excel attendance report."""
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    if not start or not end:
        return jsonify({'error': 'Parameter start_date dan end_date wajib diisi.'}), 400

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    filepath = generate_excel_report(start_date, end_date)
    return send_file(filepath, as_attachment=True)


@api_bp.route('/statistics', methods=['GET'])
@login_required
@dosen_required
def get_statistics():
    """Get overall attendance statistics."""
    from app.utils.helpers import today_wita
    from app.utils.constants import STATUS_HADIR, STATUS_TERLAMBAT

    today = today_wita()

    total_mahasiswa = User.query.filter_by(role='mahasiswa', is_active=True).count()

    today_records = Attendance.query.filter_by(
        attendance_date=today, is_valid=True
    ).all()

    hadir = sum(1 for r in today_records if r.status in (STATUS_HADIR, STATUS_TERLAMBAT))
    terlambat = sum(1 for r in today_records if r.status == STATUS_TERLAMBAT)

    return jsonify({
        'total_mahasiswa': total_mahasiswa,
        'hadir_hari_ini': hadir,
        'terlambat_hari_ini': terlambat,
        'alpha_hari_ini': total_mahasiswa - hadir,
    })


# ==========================================
# ADMIN PORTAL API ENDPOINTS
# ==========================================

@api_bp.route('/admin/users/template-excel', methods=['GET'])
@login_required
@admin_required
def get_template_excel():
    """Download template Excel for bulk student import."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Data Mahasiswa'

    headers = ['NIM', 'Nama Lengkap', 'Email', 'Kampus/Instansi', 'No HP']
    ws.append(headers)

    # Add sample rows
    ws.append(['2022001', 'Budi Santoso', 'budi.santoso@example.com', 'Universitas Hasanuddin', '081234567890'])
    ws.append(['2022002', 'Siti Aminah', 'siti.aminah@example.com', 'Universitas Negeri Makassar', '081987654321'])

    # Auto adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 15)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        download_name='template_mahasiswa.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@api_bp.route('/admin/users/import-excel', methods=['POST'])
@login_required
@admin_required
def import_excel_users():
    """Import users from uploaded Excel file."""
    if 'file' not in request.files:
        return jsonify({'error': 'File Excel tidak ditemukan.'}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Format file harus .xlsx atau .xls.'}), 400

    result = import_users_from_excel(file.stream)
    if result.get('errors') and result.get('success_count') == 0 and result.get('updated_count') == 0:
        return jsonify({'error': result['errors'][0], 'details': result['errors']}), 400

    Log.log(
        action='import_excel',
        detail=f"Import Excel Mahasiswa: {result['success_count']} akun baru, {result['updated_count']} diupdate.",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({
        'success': True,
        'message': f"Berhasil mengimpor {result['success_count']} mahasiswa baru ({result['updated_count']} diupdate, {result['skipped_count']} dilewati).",
        'data': result
    })


@api_bp.route('/admin/users/add', methods=['POST'])
@login_required
@admin_required
def add_user_manual():
    """Add a user (mahasiswa or dosen) manually."""
    data = request.get_json() or request.form
    username = str(data.get('username') or '').strip().lower()
    full_name = str(data.get('full_name') or '').strip()
    email = str(data.get('email') or '').strip().lower()
    role = str(data.get('role') or 'mahasiswa').strip().lower()
    password = str(data.get('password') or '').strip()
    nim = str(data.get('nim') or '').strip() if role == 'mahasiswa' else None
    instansi = str(data.get('instansi') or '').strip() or None
    phone = str(data.get('phone') or '').strip() or None

    if not username or not full_name or not email or not password:
        return jsonify({'error': 'Username, Nama Lengkap, Email, dan Password wajib diisi.'}), 400

    user, err = create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role=role,
        nim=nim,
        instansi=instansi,
        phone=phone
    )

    if err:
        return jsonify({'error': err}), 400

    Log.log(
        action='create_user',
        detail=f"Membuat akun {role} baru: {username}",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({
        'success': True,
        'message': f"Akun {role} ({full_name}) berhasil dibuat.",
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        }
    })


@api_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def admin_reset_password(user_id):
    """Reset a user's password to default."""
    data = request.get_json() or {}
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan.'}), 404

    default_pw = data.get('password') or ('dosen123' if user.role == 'dosen' else 'mhs123')
    success, msg = reset_user_password(user_id, default_pw)
    if not success:
        return jsonify({'error': msg}), 400

    Log.log(
        action='reset_password',
        detail=f"Mereset password user: {user.username}",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({'success': True, 'message': msg})


@api_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_status(user_id):
    """Toggle a user's active status."""
    success, msg, is_active = toggle_user_status(user_id)
    if not success:
        return jsonify({'error': msg}), 400

    user = db.session.get(User, user_id)
    Log.log(
        action='toggle_status',
        detail=f"Mengubah status {user.username} menjadi {'Aktif' if is_active else 'Nonaktif'}",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({'success': True, 'message': msg, 'is_active': is_active})


@api_bp.route('/admin/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user account."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan.'}), 404

    username = user.username
    success, msg = delete_user(user_id)
    if not success:
        return jsonify({'error': msg}), 400

    Log.log(
        action='delete_user',
        detail=f"Menghapus user: {username}",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({'success': True, 'message': msg})


@api_bp.route('/admin/users/<int:user_id>/update', methods=['POST', 'PUT'])
@login_required
@admin_required
def admin_update_user(user_id):
    """Update a user profile directly from Admin Portal."""
    data = request.get_json() or request.form
    success, msg, user = update_user_profile(user_id, data)
    if not success:
        return jsonify({'error': msg}), 400

    Log.log(
        action='update_user',
        detail=f"Memperbarui profil user: {user.username}",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({
        'success': True,
        'message': msg,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'nim': user.nim,
            'instansi': user.instansi,
            'phone': user.phone,
        }
    })


@api_bp.route('/admin/settings/update', methods=['POST'])
@login_required
@admin_required
def admin_update_settings():
    """Update system settings (geofence and time bounds)."""
    data = request.get_json() or request.form

    allowed_keys = [
        'GEOFENCE_LAT', 'GEOFENCE_LNG', 'GEOFENCE_RADIUS', 'MAX_GPS_ACCURACY',
        'CHECKIN_START', 'CHECKIN_END', 'CHECKOUT_START', 'CHECKOUT_END',
        'ENABLE_WIFI_VALIDATION', 'OFFICE_WIFI_IP'
    ]

    updated_count = 0
    for k in allowed_keys:
        if k in data and data[k] is not None:
            Setting.set(k, str(data[k]).strip())
            updated_count += 1

    if updated_count == 0:
        return jsonify({'error': 'Tidak ada pengaturan yang dikirim.'}), 400

    Log.log(
        action='update_setting',
        detail=f"Memperbarui {updated_count} konfigurasi sistem.",
        user_id=current_user.id,
        ip_address=request.remote_addr,
    )

    return jsonify({'success': True, 'message': 'Pengaturan sistem berhasil diperbarui.'})
