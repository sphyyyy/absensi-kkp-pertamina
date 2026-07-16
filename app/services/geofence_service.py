from math import radians, cos, sin, asin, sqrt

from flask import current_app


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points using
    the Haversine formula.

    Args:
        lat1, lon1: Coordinates of point 1 (degrees).
        lat2, lon2: Coordinates of point 2 (degrees).

    Returns:
        Distance in meters.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Earth's radius in meters
    r = 6_371_000
    return c * r


def is_within_geofence(latitude, longitude):
    """Check if the given coordinates are within the configured geofence radius.

    Returns:
        tuple: (is_valid: bool, distance_meters: float)
    """
    from app.models import Setting
    office_lat = float(Setting.get('GEOFENCE_LAT', current_app.config['GEOFENCE_LATITUDE']))
    office_lon = float(Setting.get('GEOFENCE_LNG', current_app.config['GEOFENCE_LONGITUDE']))
    radius = float(Setting.get('GEOFENCE_RADIUS', current_app.config['GEOFENCE_RADIUS_METERS']))

    distance = haversine_distance(latitude, longitude, office_lat, office_lon)
    return distance <= radius, round(distance, 1)


def validate_office_wifi(client_ip):
    """Check if the client IP matches the configured Office Wi-Fi IP when enabled.

    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    """
    from app.models import Setting
    enable_wifi = Setting.get('ENABLE_WIFI_VALIDATION', 'false').lower() in ('true', '1', 'yes', 'on')
    if not enable_wifi:
        return True, None

    office_ip = Setting.get('OFFICE_WIFI_IP', '').strip()
    if not office_ip:
        # If enabled but no IP configured yet, allow
        return True, None

    # Check exact match or subnet startswith (e.g. if office_ip is "192.168.1." or exact "180.252.10.5")
    if office_ip.endswith('.'):
        if client_ip.startswith(office_ip):
            return True, None
    else:
        if client_ip == office_ip:
            return True, None

    return False, f"❌ Absensi Ditolak: HP Anda tidak terhubung ke Wi-Fi Ruangan KKP Pertamina (IP saat ini: {client_ip}, Wajib ke IP: {office_ip}). Silakan sambungkan Wi-Fi kantor dan coba lagi."
