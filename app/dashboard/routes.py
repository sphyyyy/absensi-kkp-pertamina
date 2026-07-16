from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import timedelta

from app.models import Attendance, User, Setting, Log
from app.services.attendance_service import (
    get_today_attendance, get_user_attendance_history, get_user_statistics
)
from app.utils.decorators import mahasiswa_required, dosen_required, admin_required
from app.utils.helpers import (
    greeting, today_wita, now_wita, format_date, format_time
)
from app.utils.constants import STATUS_HADIR, STATUS_TERLAMBAT

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Redirect to the appropriate dashboard based on user role."""
    if current_user.role == 'admin':
        return admin_dashboard()
    if current_user.role == 'dosen':
        return dosen_dashboard()
    return mahasiswa_dashboard()


@dashboard_bp.route('/mahasiswa')
@login_required
@mahasiswa_required
def mahasiswa_dashboard():
    """Mahasiswa dashboard — mobile-first design."""
    today = today_wita()
    record = get_today_attendance(current_user.id)
    stats = get_user_statistics(current_user.id)

    # Riwayat minggu ini
    week_start = today - timedelta(days=today.weekday())
    weekly_records = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.attendance_date >= week_start,
        Attendance.attendance_date <= today,
    ).order_by(Attendance.attendance_date.desc()).all()

    return render_template(
        'mahasiswa/dashboard.html',
        greeting=greeting(),
        today=today,
        today_formatted=format_date(today),
        record=record,
        stats=stats,
        weekly_records=weekly_records,
        format_time=format_time,
        format_date=format_date,
    )


@dashboard_bp.route('/mahasiswa/riwayat')
@login_required
@mahasiswa_required
def mahasiswa_history():
    """Mahasiswa attendance history page."""
    history = get_user_attendance_history(current_user.id, limit=50)
    stats = get_user_statistics(current_user.id)

    return render_template(
        'mahasiswa/history.html',
        history=history,
        stats=stats,
        format_time=format_time,
        format_date=format_date,
    )


@dashboard_bp.route('/dosen')
@login_required
@dosen_required
def dosen_dashboard():
    """Dosen dashboard — desktop-optimized design."""
    today = today_wita()

    # Summary statistics
    total_mahasiswa = User.query.filter_by(role='mahasiswa', is_active=True).count()

    today_records = Attendance.query.filter_by(
        attendance_date=today, is_valid=True
    ).all()

    hadir_count = sum(1 for r in today_records if r.status in (STATUS_HADIR, STATUS_TERLAMBAT))
    terlambat_count = sum(1 for r in today_records if r.status == STATUS_TERLAMBAT)
    alpha_count = total_mahasiswa - hadir_count

    # Recent attendance records
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search = request.args.get('search', '').strip()
    filter_date = request.args.get('date', '')

    query = (
        Attendance.query
        .join(User)
        .filter(Attendance.is_valid == True)  # noqa: E712
    )

    if filter_date:
        query = query.filter(Attendance.attendance_date == filter_date)
    else:
        query = query.filter(Attendance.attendance_date == today)

    if search:
        query = query.filter(
            User.full_name.ilike(f'%{search}%') |
            User.nim.ilike(f'%{search}%')
        )

    pagination = query.order_by(
        Attendance.attendance_date.desc(), User.full_name
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Weekly data for chart (last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d/%m'))
        count = Attendance.query.filter(
            Attendance.attendance_date == d,
            Attendance.is_valid == True,  # noqa: E712
            Attendance.status.in_([STATUS_HADIR, STATUS_TERLAMBAT])
        ).count()
        chart_data.append(count)

    return render_template(
        'dosen/dashboard.html',
        today=today,
        today_formatted=format_date(today),
        total_mahasiswa=total_mahasiswa,
        hadir_count=hadir_count,
        terlambat_count=terlambat_count,
        alpha_count=alpha_count,
        pagination=pagination,
        search=search,
        filter_date=filter_date,
        chart_labels=chart_labels,
        chart_data=chart_data,
        format_time=format_time,
        format_date=format_date,
    )


@dashboard_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Administrator portal dashboard for user management & runtime settings."""
    mahasiswa_list = User.query.filter_by(role='mahasiswa').order_by(User.full_name).all()
    dosen_list = User.query.filter_by(role='dosen').order_by(User.full_name).all()
    settings = Setting.query.order_by(Setting.key).all()
    settings_dict = {s.key: s.value for s in settings}
    logs = Log.query.order_by(Log.created_at.desc()).limit(100).all()

    return render_template(
        'dashboard/admin.html',
        mahasiswa_list=mahasiswa_list,
        dosen_list=dosen_list,
        settings_dict=settings_dict,
        logs=logs,
        format_date=format_date,
        format_time=format_time,
    )

