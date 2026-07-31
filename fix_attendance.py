"""Script untuk mengubah status attendance dari 'terlambat' -> 'hadir'."""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models import User, Attendance
from app.utils.constants import STATUS_HADIR, STATUS_TERLAMBAT


def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print("=== DAFTAR USER ===")
        for u in users:
            count_terlambat = Attendance.query.filter_by(user_id=u.id, status=STATUS_TERLAMBAT).count()
            count_hadir = Attendance.query.filter_by(user_id=u.id, status=STATUS_HADIR).count()
            print(f"  ID={u.id} | username={u.username} | role={u.role} | hadir={count_hadir} | terlambat={count_terlambat}")


def fix_attendance(username='odief'):
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"[ERROR] User '{username}' tidak ditemukan.")
            return

        print(f"[OK] User: {user.full_name} (ID: {user.id})")

        records = Attendance.query.filter_by(
            user_id=user.id,
            status=STATUS_TERLAMBAT
        ).all()

        if not records:
            print("[INFO] Tidak ada record 'terlambat' untuk user ini.")
            return

        print(f"\n[INFO] Ditemukan {len(records)} record 'terlambat':")
        for r in records:
            print(f"   - Tanggal: {r.attendance_date} | Check-in: {r.check_in_time}")

        for r in records:
            r.status = STATUS_HADIR

        db.session.commit()
        print(f"\n[OK] Berhasil diubah {len(records)} record -> 'hadir'.")


if __name__ == '__main__':
    list_users()
    print()
    fix_attendance('odief')
