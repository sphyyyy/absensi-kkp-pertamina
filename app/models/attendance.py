from app.extensions import db
from app.utils.helpers import now_wita


class Attendance(db.Model):
    """Attendance record for check-in and check-out."""

    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Date and times
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)

    # GPS data — check-in
    latitude_in = db.Column(db.Float, nullable=True)
    longitude_in = db.Column(db.Float, nullable=True)
    accuracy_in = db.Column(db.Float, nullable=True)

    # GPS data — check-out
    latitude_out = db.Column(db.Float, nullable=True)
    longitude_out = db.Column(db.Float, nullable=True)
    accuracy_out = db.Column(db.Float, nullable=True)

    # Photos
    photo_in = db.Column(db.String(255), nullable=True)
    photo_out = db.Column(db.String(255), nullable=True)

    # Device info
    ip_address_in = db.Column(db.String(45), nullable=True)
    ip_address_out = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)

    # Status
    status = db.Column(db.String(20), nullable=False, default='hadir')
    notes = db.Column(db.Text, nullable=True)
    is_valid = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=now_wita)

    # Composite index for fast lookup: user + date
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'attendance_date'),
    )

    @property
    def has_checked_in(self):
        return self.check_in_time is not None

    @property
    def has_checked_out(self):
        return self.check_out_time is not None

    @property
    def is_complete(self):
        return self.has_checked_in and self.has_checked_out

    def __repr__(self):
        return f'<Attendance user={self.user_id} date={self.attendance_date} status={self.status}>'
