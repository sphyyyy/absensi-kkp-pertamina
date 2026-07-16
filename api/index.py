import sys
import os

# Tambahkan direktori root proyek ke `sys.path` agar modul `app` dapat di-import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()
_db_initialized = False


@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            db.create_all()
            _db_initialized = True
        except Exception as e:
            print(f"[Warning] Gagal inisialisasi tabel database saat request Vercel: {e}")

