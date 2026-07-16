from datetime import datetime, time, timezone, timedelta

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


def format_date_id(d):
    """Format date to Indonesian style: DD Month YYYY."""
    if d is None:
        return '-'
    months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
    ]
    return f'{d.day:02d} {months[d.month - 1]} {d.year}'


def format_datetime_id(dt):
    """Format datetime to Indonesian style."""
    if dt is None:
        return '-'
    return f'{format_date_id(dt.date())} {dt.strftime("%H:%M")} WITA'


# Backwards compatibility aliases
format_date = format_date_id
format_datetime = format_datetime_id



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


def clean_time_string(time_str, default='07:00'):
    """Clean and normalize time string to 'HH:MM' format safely (e.g. '23.000' -> '23:00')."""
    if not time_str or not isinstance(time_str, str):
        return default
    cleaned = time_str.strip().replace('.', ':').replace(',', ':').replace(';', ':')
    parts = [p for p in cleaned.split(':') if p != '']
    try:
        hour = int(parts[0][:2]) if len(parts) > 0 else 0
        minute = int(parts[1][:2]) if len(parts) > 1 else 0
        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))
        return f'{hour:02d}:{minute:02d}'
    except (ValueError, IndexError, AttributeError):
        return default


def parse_time_string(time_str):
    """Parse 'HH:MM' string to time object without raising exceptions."""
    cleaned = clean_time_string(time_str, default='00:00')
    try:
        parts = cleaned.split(':')
        return time(int(parts[0]), int(parts[1]))
    except Exception:
        return time(0, 0)


def calculate_attendance_percentage(total_days, present_days):
    """Calculate attendance percentage safely."""
    if total_days == 0:
        return 0.0
    return round((present_days / total_days) * 100, 1)
