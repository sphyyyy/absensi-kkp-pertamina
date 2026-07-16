from app.extensions import db
from app.utils.helpers import now_wita


class Log(db.Model):
    """Activity audit log for security tracking."""

    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=now_wita, index=True)

    @staticmethod
    def log(action, detail=None, user_id=None, ip_address=None):
        """Create a new log entry."""
        entry = Log(
            user_id=user_id,
            action=action,
            detail=detail,
            ip_address=ip_address
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    def __repr__(self):
        return f'<Log {self.action} by user={self.user_id}>'
