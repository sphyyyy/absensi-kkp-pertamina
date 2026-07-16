from typing import Any
from app.extensions import db
from app.utils.helpers import now_wita


class Setting(db.Model):
    """Key-value configuration store for runtime settings."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=now_wita, onupdate=now_wita)

    @staticmethod
    def get(key, default=None):
        """Get a setting value by key (case-insensitive)."""
        if not key:
            return default
        key_upper = str(key).strip().upper()
        setting = Setting.query.filter(db.func.upper(Setting.key) == key_upper).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value, description=None):
        """Set or update a setting value (always normalized to UPPERCASE)."""
        if not key:
            return None
        key_upper = str(key).strip().upper()
        setting = Setting.query.filter(db.func.upper(Setting.key) == key_upper).first()
        if setting:
            setting.key = key_upper
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = Setting(key=key_upper, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def normalize_keys():
        """Normalize all database setting keys to uppercase and deduplicate if needed."""
        try:
            settings = Setting.query.all()
            if not settings:
                return
            seen = {}
            dirty = False
            for s in settings:
                k_upper = s.key.strip().upper()
                if k_upper in seen:
                    if s.key == k_upper:
                        old_s = seen[k_upper]
                        db.session.delete(old_s)
                        seen[k_upper] = s
                        dirty = True
                    else:
                        db.session.delete(s)
                        dirty = True
                else:
                    if s.key != k_upper:
                        s.key = k_upper
                        dirty = True
                    seen[k_upper] = s
            if dirty:
                db.session.commit()
        except Exception:
            db.session.rollback()

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
