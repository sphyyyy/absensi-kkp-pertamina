import os
import time
from threading import Thread
from pycloudflared import try_cloudflare
from app import create_app
from app.extensions import db

app = create_app()

def start_flask():
    with app.app_context():
        db.create_all()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    print("=================================================================")
    print("  MEMULAI SERVER ABSENSI PERTAMINA DENGAN HTTPS PUBLIC TUNNEL    ")
    print("=================================================================")
    
    # Start Flask server in background thread
    t = Thread(target=start_flask, daemon=True)
    t.start()
    time.sleep(2)  # Give Flask 2 seconds to bind to port 5000

    print("--> Menghubungkan ke Cloudflare Edge Network (HTTPS Tunnel)...")
    tunnel = try_cloudflare(port=5000)
    
    print("\n" + "="*65)
    print("✅ TUNNEL HTTPS BERHASIL DIAKTIFKAN!")
    print(f"👉 LINK AKSES UNTUK HP MAHASISWA : {tunnel.tunnel}")
    print("="*65 + "\n")
    print("Tekan Ctrl+C di terminal ini untuk menghentikan server.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMenutup server...")
