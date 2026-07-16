import os
import logging

from flask import Flask, render_template

from app.config import config_map
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    """Application factory for the KKP Attendance System.

    Args:
        config_name: 'development', 'production', or 'testing'.

    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register context processors
    _register_context_processors(app)

    # Configure logging
    _configure_logging(app)

    # Ensure required directories exist
    _ensure_directories(app)

    return app


def _init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))


def _register_blueprints(app):
    """Register all Flask blueprints."""
    from app.auth import auth_bp
    from app.attendance import attendance_bp
    from app.dashboard import dashboard_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Root route redirects to dashboard
    @app.route('/')
    def root():
        from flask_login import current_user
        if current_user.is_authenticated:
            from flask import redirect, url_for
            return redirect(url_for('dashboard.index'))
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))


def _register_error_handlers(app):
    """Register custom error pages."""

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500


def _register_context_processors(app):
    """Register Jinja2 context processors available in all templates."""

    @app.context_processor
    def inject_globals():
        from app.utils.helpers import now_wita
        return {
            'current_year': now_wita().year,
            'app_name': 'Absensi KKP',
            'company_name': 'PT. Pertamina Patra Niaga Regional Sulawesi',
        }


def _configure_logging(app):
    """Set up application logging."""
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


def _ensure_directories(app):
    """Create required directories if they don't exist (safe for Vercel/cloud read-only filesystem)."""
    from app.config import is_serverless_env
    is_serverless = is_serverless_env()
    dirs = [
        app.config.get('UPLOAD_FOLDER', '/tmp/selfies' if is_serverless else 'uploads/selfies'),
        '/tmp/reports' if is_serverless else 'reports',
    ]
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as e:
            # Di serverless Vercel, abaikan error jika mencoba membuat folder di sistem file read-only
            app.logger.warning(f"Could not create directory {d}: {e}")

