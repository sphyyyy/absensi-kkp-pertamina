import sys
import time
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    print("=" * 65, flush=True)
    print(">>> MEMULAI NGROK HTTPS TUNNEL (SECURE CONTEXT GPS) <<<", flush=True)
    print("=" * 65, flush=True)
    print("[*] Memastikan server lokal Flask (port 5000) berjalan...", flush=True)
    print("[*] Menghubungkan ke jaringan Ngrok menggunakan Authtoken Anda...", flush=True)

    try:
        from pyngrok import ngrok
        # Pastikan authtoken terkonfigurasi
        ngrok.set_auth_token("3GZ0yeX4s7D2AvNEQkhhVtGCP22_6V5tPaoctxt9TiQQzaMsa")
        
        # Buka tunnel ke port 5000
        tunnel = ngrok.connect(5000, bind_tls=True)
        url = tunnel.public_url

        print("\n" + "★" * 65, flush=True)
        print(" ✅ LINK NGROK HTTPS BERHASIL DIBUAT (GPS HP FULLY ENABLED) ✅", flush=True)
        print("★" * 65, flush=True)
        print(f"\n  👉  LINK RESMI ANDA :  {url}  👈\n", flush=True)
        print("-----------------------------------------------------------------", flush=True)
        print(" 📱 CARA MENGGUNAKAN DI SMARTPHONE ANDA:", flush=True)
        print(" 1. Buka browser Chrome / Safari di HP Anda.", flush=True)
        print(f" 2. Ketik / tempel link di atas: {url}", flush=True)
        print(" 3. Jika muncul halaman selamat datang Ngrok, klik 'Visit Site'.", flush=True)
        print(" 4. Login dengan akun Anda & klik tombol Absen Masuk.", flush=True)
        print(" 5. GPS / Lokasi akan LANGSUNG TERDETEKSI akurat (Karena HTTPS!).", flush=True)
        print("-----------------------------------------------------------------", flush=True)
        print(" (*) Tekan Ctrl+C di jendela ini jika ingin menutup tunnel.\n", flush=True)

        # Tahan proses agar tunnel tetap hidup sampai user menekan Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Menutup Ngrok Tunnel...", flush=True)
            ngrok.disconnect(url)
            ngrok.kill()
            print("[*] Tunnel ditutup.", flush=True)

    except Exception as e:
        print(f"\n[X] Gagal memulai Ngrok: {e}", flush=True)
        print("[*] Mencoba fallback ke Cloudflare Tunnel...", flush=True)
        import subprocess, re
        cloudflared_path = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "cloudflared.exe")
        if not os.path.exists(cloudflared_path):
            cloudflared_path = "cloudflared.exe"
        process = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1
        )
        url_found = False
        try:
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match and not url_found:
                    url_found = True
                    url = match.group(0)
                    print(f"\n  👉  LINK CLOUDFLARE :  {url}  👈\n", flush=True)
        except KeyboardInterrupt:
            process.terminate()

if __name__ == "__main__":
    main()
