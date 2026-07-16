import sys
import os

# Tambahkan direktori root proyek ke `sys.path` agar modul `app` dapat di-import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402

app = create_app()
_db_initialized = False


@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            db.create_all()
            from app.models import User
            if not User.query.first():
                from seed import seed
                seed()
                print("[Info] Auto-seed Vercel berhasil dijalankan (admin, dosen1, mhs1 siap)!")
            from app.models import Setting
            Setting.normalize_keys()
            _db_initialized = True
        except Exception as e:
            db.session.rollback()
            print(f"[Warning] Gagal inisialisasi / auto-seed tabel database saat request Vercel: {e}")


