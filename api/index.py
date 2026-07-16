import sys
import os

# Tambahkan direktori root proyek ke `sys.path` agar modul `app` dapat di-import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()

# Di lingkungan serverless, pastikan tabel dibuat/diperiksa pada request context bila belum ada
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"[Warning] Gagal inisialisasi tabel database saat startup Vercel: {e}")
