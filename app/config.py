import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def is_serverless_env():
    """Mendeteksi apakah aplikasi berjalan di lingkungan Serverless / Read-Only (Vercel, AWS Lambda, /var/task)."""
    return bool(
        os.getenv('VERCEL')
        or os.getenv('VERCEL_ENV')
        or os.getenv('AWS_LAMBDA_FUNCTION_NAME')
        or os.getenv('NOW_REGION')
        or ('/var/task' in os.path.abspath(__file__).replace('\\', '/'))
    )


def get_database_uri(default_sqlite='sqlite:///absensi_kkp.db'):
    """Mengambil URI database dari environment dan melakukan normalisasi untuk Vercel & PostgreSQL."""
    db_uri = os.getenv('DATABASE_URL')
    if db_uri:
        if db_uri.startswith('postgres://'):
            db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
        return db_uri
    # Di lingkungan serverless tanpa DATABASE_URL, gunakan /tmp/ agar sistem file tidak error Read-Only
    if is_serverless_env():
        return 'sqlite:////tmp/absensi_kkp.db'
    return default_sqlite


class BaseConfig:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv('SESSION_LIFETIME_MINUTES', 480))
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE_MB', 5)) * 1024 * 1024
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        '/tmp/selfies' if is_serverless_env() else 'uploads/selfies'
    )
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Geofence — PT. Pertamina Patra Niaga Regional Sulawesi
    GEOFENCE_LATITUDE = float(os.getenv('GEOFENCE_LATITUDE', -5.1477))
    GEOFENCE_LONGITUDE = float(os.getenv('GEOFENCE_LONGITUDE', 119.4327))
    GEOFENCE_RADIUS_METERS = float(os.getenv('GEOFENCE_RADIUS_METERS', 100))

    # Waktu Absensi (WITA / UTC+8)
    CHECKIN_START = os.getenv('CHECKIN_START', '07:00')
    CHECKIN_END = os.getenv('CHECKIN_END', '09:00')
    CHECKOUT_START = os.getenv('CHECKOUT_START', '16:00')
    CHECKOUT_END = os.getenv('CHECKOUT_END', '18:00')

    # Timezone offset (WITA = UTC+8)
    TIMEZONE_OFFSET_HOURS = 8


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_database_uri('sqlite:///absensi_kkp.db')
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    """Production configuration with strict security."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_database_uri('sqlite:///absensi_kkp.db')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax' if is_serverless_env() else 'Strict'




class TestingConfig(BaseConfig):
    """Testing configuration with in-memory database."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
