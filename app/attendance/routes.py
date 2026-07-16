from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.services.attendance_service import process_checkin, process_checkout, get_today_attendance
from app.utils.decorators import mahasiswa_required
from app.utils.helpers import format_time

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/check-in', methods=['POST'])
@login_required
@mahasiswa_required
def check_in():
    """Process check-in request via AJAX."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Data tidak valid.'}), 400

    success, message = process_checkin(current_user.id, data)
    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code


@attendance_bp.route('/check-out', methods=['POST'])
@login_required
@mahasiswa_required
def check_out():
    """Process check-out request via AJAX."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Data tidak valid.'}), 400

    success, message = process_checkout(current_user.id, data)
    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code


@attendance_bp.route('/status', methods=['GET'])
@login_required
@mahasiswa_required
def status():
    """Get today's attendance status for the current user."""
    record = get_today_attendance(current_user.id)

    if not record:
        return jsonify({
            'checked_in': False,
            'checked_out': False,
            'check_in_time': None,
            'check_out_time': None,
            'status': None,
        })

    return jsonify({
        'checked_in': record.has_checked_in,
        'checked_out': record.has_checked_out,
        'check_in_time': format_time(record.check_in_time),
        'check_out_time': format_time(record.check_out_time),
        'status': record.status,
    })
