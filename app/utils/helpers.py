from datetime import datetime, timezone, timedelta

# WITA timezone (UTC+8)
WITA = timezone(timedelta(hours=8))


def now_wita():
    """Get current datetime in WITA timezone."""
    return datetime.now(WITA)


def today_wita():
    """Get current date in WITA timezone."""
    return now_wita().date()


def greeting():
    """Generate time-based Indonesian greeting."""
    hour = now_wita().hour
    if hour < 11:
        return 'Selamat Pagi'
    elif hour < 15:
        return 'Selamat Siang'
    elif hour < 18:
        return 'Selamat Sore'
    return 'Selamat Malam'


def format_time(t):
    """Format time object to HH:MM string."""
    if t is None:
        return '-'
    return t.strftime('%H:%M')


def format_date(d):
    """Format date to Indonesian-style string (e.g. '15 Juli 2026')."""
    if d is None:
        return '-'
    months = [
        '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    return f'{d.day} {months[d.month]} {d.year}'


def format_datetime(dt):
    """Format datetime to Indonesian-style string."""
    if dt is None:
        return '-'
    return f'{format_date(dt.date())} {format_time(dt.time())}'


def allowed_file(filename, allowed_extensions):
    """Check if filename has an allowed extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    )


def generate_filename(user_id, attendance_type):
    """Generate a unique filename for selfie photos."""
    timestamp = now_wita().strftime('%Y%m%d_%H%M%S')
    return f'{user_id}_{attendance_type}_{timestamp}.jpg'


def parse_time_string(time_str):
    """Parse 'HH:MM' string to time object."""
    parts = time_str.strip().split(':')
    return datetime.strptime(f'{parts[0]}:{parts[1]}', '%H:%M').time()


def calculate_attendance_percentage(total_days, present_days):
    """Calculate attendance percentage safely."""
    if total_days == 0:
        return 0.0
    return round((present_days / total_days) * 100, 1)
