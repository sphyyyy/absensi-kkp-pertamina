from app.extensions import db
from app.utils.helpers import now_wita


class Setting(db.Model):
    """Key-value configuration store for runtime settings."""

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=now_wita, onupdate=now_wita)

    @staticmethod
    def get(key, default=None):
        """Get a setting value by key."""
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value, description=None):
        """Set or update a setting value."""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
