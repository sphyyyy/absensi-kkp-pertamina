import base64
from datetime import datetime, timedelta

from flask import current_app, request as flask_request

from app.extensions import db
from app.models import Attendance, Log, Setting
from app.services.geofence_service import is_within_geofence
from app.services.photo_service import validate_photo, save_photo
from app.utils.helpers import now_wita, today_wita, parse_time_string
from app.utils.constants import (
    STATUS_HADIR, STATUS_TERLAMBAT,
    TYPE_CHECKIN, TYPE_CHECKOUT,
    ERR_OUTSIDE_GEOFENCE, ERR_OUTSIDE_TIME_WINDOW,
    ERR_ALREADY_CHECKED_IN, ERR_ALREADY_CHECKED_OUT,
    ERR_NOT_CHECKED_IN,
    ERR_GPS_REQUIRED, ERR_GPS_LOW_ACCURACY,
    MSG_CHECKIN_SUCCESS, MSG_CHECKOUT_SUCCESS,
    MAX_GPS_ACCURACY_METERS,
)


def _get_client_ip():
    """Extract the client IP, respecting X-Forwarded-For for proxies."""
    forwarded = flask_request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return flask_request.remote_addr


def _validate_time_window(attendance_type):
    """Check if the current time falls within the allowed window.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        db.session.expire_all()
    except Exception:
        pass
    now = now_wita().time()

    if attendance_type == TYPE_CHECKIN:
        start = parse_time_string(Setting.get('CHECKIN_START', current_app.config['CHECKIN_START']))
        end = parse_time_string(Setting.get('CHECKIN_END', current_app.config['CHECKIN_END']))
    else:
        start = parse_time_string(Setting.get('CHECKOUT_START', current_app.config['CHECKOUT_START']))
        end = parse_time_string(Setting.get('CHECKOUT_END', current_app.config['CHECKOUT_END']))

    if start <= now <= end:
        return True, None

    label = 'masuk' if attendance_type == TYPE_CHECKIN else 'pulang'
    return False, (
        f'{ERR_OUTSIDE_TIME_WINDOW} '
        f'Jam absen {label}: {start.strftime("%H:%M")} - {end.strftime("%H:%M")}.'
    )


def _is_late(attendance_type):
    """Determine if the check-in is late (after CHECKIN_START + 30 min buffer)."""
    if attendance_type != TYPE_CHECKIN:
        return False
    try:
        db.session.expire_all()
    except Exception:
        pass
    now = now_wita().time()
    start = parse_time_string(Setting.get('CHECKIN_START', current_app.config['CHECKIN_START']))
    # Consider late if checked in after 30 minutes past start
    late_threshold = datetime.combine(
        today_wita(), start
    ) + timedelta(minutes=30)
    return now > late_threshold.time()


def get_today_attendance(user_id):
    """Get today's attendance record for a user, if any."""
    return Attendance.query.filter_by(
        user_id=user_id,
        attendance_date=today_wita()
    ).first()


def process_checkin(user_id, data):
    """Process a check-in request with full validation pipeline.

    Args:
        user_id: ID of the authenticated user.
        data: dict with keys: latitude, longitude, accuracy, photo (base64).

    Returns:
        tuple: (success: bool, message: str)
    """
    # 1. Validate GPS data presence
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')

    if latitude is None or longitude is None:
        return False, ERR_GPS_REQUIRED

    latitude = float(latitude)
    longitude = float(longitude)
    accuracy = float(accuracy) if accuracy else 999

    # 2. Validate GPS accuracy
    max_acc = float(Setting.get('MAX_GPS_ACCURACY', MAX_GPS_ACCURACY_METERS))
    if accuracy > max_acc:
        return False, f"{ERR_GPS_LOW_ACCURACY} (Akurasi terdeteksi: {int(accuracy)}m, Batas maksimal: {int(max_acc)}m)"

    # 3. Validate time window
    time_ok, time_err = _validate_time_window(TYPE_CHECKIN)
    if not time_ok:
        return False, time_err

    # 4. Check duplicate check-in
    existing = get_today_attendance(user_id)
    if existing and existing.has_checked_in:
        return False, ERR_ALREADY_CHECKED_IN

    # 5. Validate geofence
    within, distance = is_within_geofence(latitude, longitude)
    if not within:
        radius = float(Setting.get('GEOFENCE_RADIUS', current_app.config['GEOFENCE_RADIUS_METERS']))
        return False, f'{ERR_OUTSIDE_GEOFENCE} Jarak Anda: {distance}m (Maksimal: {radius}m dari kantor Pertamina).'
    # 6. Validate and save photo (Optional / 1-Click Geofence Mode)
    photo_b64 = data.get('photo')
    if photo_b64:
        try:
            photo_bytes = base64.b64decode(photo_b64)
            photo_valid, photo_err = validate_photo(photo_bytes)
            if photo_valid:
                filename = save_photo(photo_bytes, user_id, TYPE_CHECKIN)
            else:
                filename = '1-click-geofence'
        except Exception:
            filename = '1-click-geofence'
    else:
        filename = '1-click-geofence'

    # 7. Determine status (hadir or terlambat)
    status = STATUS_TERLAMBAT if _is_late(TYPE_CHECKIN) else STATUS_HADIR

    # 8. Save attendance record
    now = now_wita()
    if existing:
        # Update existing record (edge case: record created for 'izin')
        existing.check_in_time = now.time()
        existing.latitude_in = latitude
        existing.longitude_in = longitude
        existing.accuracy_in = accuracy
        existing.photo_in = filename
        existing.ip_address_in = _get_client_ip()
        existing.user_agent = flask_request.headers.get('User-Agent', '')[:500]
        existing.status = status
        existing.is_valid = True
    else:
        attendance = Attendance(
            user_id=user_id,
            attendance_date=today_wita(),
            check_in_time=now.time(),
            latitude_in=latitude,
            longitude_in=longitude,
            accuracy_in=accuracy,
            photo_in=filename,
            ip_address_in=_get_client_ip(),
            user_agent=flask_request.headers.get('User-Agent', '')[:500],
            status=status,
            is_valid=True,
        )
        db.session.add(attendance)

    db.session.commit()

    # 9. Log activity
    Log.log(
        action='check_in',
        detail=f'Check-in at {now.strftime("%H:%M")} | Status: {status} | Distance: {distance}m',
        user_id=user_id,
        ip_address=_get_client_ip()
    )

    return True, MSG_CHECKIN_SUCCESS


def process_checkout(user_id, data):
    """Process a check-out request with full validation pipeline.

    Args:
        user_id: ID of the authenticated user.
        data: dict with keys: latitude, longitude, accuracy, photo (base64).

    Returns:
        tuple: (success: bool, message: str)
    """
    # 1. Validate GPS data
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')

    if latitude is None or longitude is None:
        return False, ERR_GPS_REQUIRED

    latitude = float(latitude)
    longitude = float(longitude)
    accuracy = float(accuracy) if accuracy else 999

    max_acc = float(Setting.get('MAX_GPS_ACCURACY', MAX_GPS_ACCURACY_METERS))
    if accuracy > max_acc:
        return False, f"{ERR_GPS_LOW_ACCURACY} (Akurasi terdeteksi: {int(accuracy)}m, Batas maksimal: {int(max_acc)}m)"

    # 2. Validate time window
    time_ok, time_err = _validate_time_window(TYPE_CHECKOUT)
    if not time_ok:
        return False, time_err

    # 3. Must have checked in first
    existing = get_today_attendance(user_id)
    if not existing or not existing.has_checked_in:
        return False, ERR_NOT_CHECKED_IN

    if existing.has_checked_out:
        return False, ERR_ALREADY_CHECKED_OUT

    # 4. Validate geofence
    within, distance = is_within_geofence(latitude, longitude)
    if not within:
        radius = float(Setting.get('GEOFENCE_RADIUS', current_app.config['GEOFENCE_RADIUS_METERS']))
        return False, f'{ERR_OUTSIDE_GEOFENCE} Jarak Anda: {distance}m (Maksimal: {radius}m dari kantor Pertamina).'
    # 5. Validate and save photo (Optional / 1-Click Geofence Mode)
    photo_b64 = data.get('photo')
    if photo_b64:
        try:
            photo_bytes = base64.b64decode(photo_b64)
            photo_valid, photo_err = validate_photo(photo_bytes)
            if photo_valid:
                filename = save_photo(photo_bytes, user_id, TYPE_CHECKOUT)
            else:
                filename = '1-click-geofence'
        except Exception:
            filename = '1-click-geofence'
    else:
        filename = '1-click-geofence'

    # 6. Update attendance record
    now = now_wita()
    existing.check_out_time = now.time()
    existing.latitude_out = latitude
    existing.longitude_out = longitude
    existing.accuracy_out = accuracy
    existing.photo_out = filename
    existing.ip_address_out = _get_client_ip()

    db.session.commit()

    # 7. Log activity
    Log.log(
        action='check_out',
        detail=f'Check-out at {now.strftime("%H:%M")} | Distance: {distance}m',
        user_id=user_id,
        ip_address=_get_client_ip()
    )

    return True, MSG_CHECKOUT_SUCCESS


def get_user_attendance_history(user_id, limit=30):
    """Get recent attendance history for a user."""
    return Attendance.query.filter_by(user_id=user_id).order_by(
        Attendance.attendance_date.desc()
    ).limit(limit).all()


def get_user_statistics(user_id):
    """Calculate attendance statistics for a user."""
    records = Attendance.query.filter_by(user_id=user_id, is_valid=True).all()

    total = len(records)
    hadir = sum(1 for r in records if r.status == STATUS_HADIR)
    terlambat = sum(1 for r in records if r.status == STATUS_TERLAMBAT)
    izin = sum(1 for r in records if r.status == 'izin')

    return {
        'total': total,
        'hadir': hadir,
        'terlambat': terlambat,
        'izin': izin,
        'persentase': round((hadir + terlambat) / total * 100, 1) if total > 0 else 0,
    }
