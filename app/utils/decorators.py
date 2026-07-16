from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """Decorator to restrict access to specific user roles.

    Usage:
        @role_required('dosen', 'admin')
        def admin_dashboard():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def mahasiswa_required(f):
    """Shortcut decorator for mahasiswa-only routes."""
    return role_required('mahasiswa')(f)


def dosen_required(f):
    """Shortcut decorator for dosen-only routes."""
    return role_required('dosen')(f)


def admin_required(f):
    """Shortcut decorator for admin-only routes."""
    return role_required('admin')(f)
