/**
 * Geolocation module for the KKP Attendance System.
 * Handles GPS permission, position acquisition, and error handling.
 */

const GeoLocation = {
    position: null,
    error: null,

    /**
     * Request current GPS position with high accuracy.
     * @returns {Promise<{latitude: number, longitude: number, accuracy: number}>}
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Browser tidak mendukung sensor GPS. Gunakan browser modern seperti Google Chrome atau Safari.'));
                return;
            }

            // Pengecekan Keamanan Browser (Modern Browser memblokir GPS di alamat HTTP non-localhost)
            if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                const isAndroid = /Android/i.test(navigator.userAgent);
                if (isAndroid) {
                    reject(new Error(`[Blokir Keamanan Browser HP] Google Chrome memblokir sensor GPS pada alamat HTTP (${window.location.hostname}).\n\nSOLUSI PERMANEN DI CHROME HP ANDA:\n1. Ketik "chrome://flags" di URL Chrome HP\n2. Cari "Insecure origins treated as secure"\n3. Aktifkan (Enable) & masukkan: http://${window.location.host}\n4. Klik "Relaunch" di Chrome HP Anda.`));
                    return;
                }
            }

            const options = {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0,
            };

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    this.position = {
                        latitude: pos.coords.latitude,
                        longitude: pos.coords.longitude,
                        accuracy: pos.coords.accuracy,
                    };
                    resolve(this.position);
                },
                (err) => {
                    let message;
                    switch (err.code) {
                        case err.PERMISSION_DENIED:
                            if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                                message = `Izin lokasi ditolak / diblokir oleh browser HP karena web ini diakses melalui jaringan HTTP (${window.location.hostname}).\n\nCARA MEMPERBAIKI PERMANEN DI CHROME HP:\n1. Buka tab baru di Chrome HP, ketik: chrome://flags\n2. Cari pengaturan: Insecure origins treated as secure\n3. Ubah ke Enabled, lalu ketik alamat web ini: http://${window.location.host}\n4. Klik tombol Relaunch di bawah layar Chrome HP Anda. Setelah itu GPS akan langsung aktif!`;
                            } else {
                                message = 'Izin lokasi ditolak. Aktifkan GPS di HP Anda dan izinkan akses lokasi pada pengaturan browser.';
                            }
                            break;
                        case err.POSITION_UNAVAILABLE:
                            message = 'Lokasi tidak tersedia. Pastikan GPS aktif.';
                            break;
                        case err.TIMEOUT:
                            message = 'Waktu permintaan lokasi habis. Coba lagi di area terbuka.';
                            break;
                        default:
                            message = 'Gagal mendapatkan lokasi: ' + err.message;
                    }
                    this.error = message;
                    reject(new Error(message));
                },
                options
            );
        });
    },
};
