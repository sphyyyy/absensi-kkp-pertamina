/**
 * Dashboard Attendance UI logic.
 */
let currentAttendanceType = 'check_in';
let gpsData = null;

/**
 * Start the attendance flow (check-in or check-out).
 */
function startAttendance(type) {
    currentAttendanceType = type;
    gpsData = null;

    // Set modal title
    const modalTitle = document.getElementById('attendanceModalLabel');
    if (modalTitle) {
        modalTitle.textContent = type === 'check_in' ? 'Absen Masuk (Geofence GPS)' : 'Absen Pulang (Geofence GPS)';
    }

    _showStep('stepGPS');

    // Show modal
    const modalEl = document.getElementById('attendanceModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }

    // Start GPS acquisition
    _acquireGPS();
}

/**
 * Step 1: Acquire GPS coordinates.
 */
async function _acquireGPS() {
    const gpsStatus = document.getElementById('gpsStatus');
    const gpsSpinner = document.getElementById('gpsSpinner');
    const gpsError = document.getElementById('gpsError');

    if (gpsStatus) gpsStatus.textContent = 'Mendeteksi lokasi GPS...';
    if (gpsSpinner) gpsSpinner.classList.remove('d-none');
    if (gpsError) gpsError.classList.add('d-none');

    try {
        gpsData = await GeoLocation.getCurrentPosition();

        if (gpsStatus) {
            gpsStatus.textContent = `Lokasi terdeteksi! (Akurasi: ±${Math.round(gpsData.accuracy)}m)`;
        }
        if (gpsSpinner) gpsSpinner.classList.add('d-none');

        // Automatically submit after short delay
        setTimeout(() => {
            _submitAttendance();
        }, 800);

    } catch (err) {
        if (gpsError) {
            gpsError.textContent = err.message;
            gpsError.classList.remove('d-none');
        }
        if (gpsSpinner) gpsSpinner.classList.add('d-none');
    }
}

/**
 * Step 2: Submit attendance data to the server (Geofence GPS).
 */
async function _submitAttendance() {
    _showStep('stepSubmit');

    const endpoint = currentAttendanceType === 'check_in'
        ? '/attendance/check-in'
        : '/attendance/check-out';

    const payload = {
        latitude: gpsData.latitude,
        longitude: gpsData.longitude,
        accuracy: gpsData.accuracy,
    };

    try {
        const result = await apiFetch(endpoint, payload);
        _showResult(result.success, result.message);
    } catch (err) {
        _showResult(false, 'Terjadi kesalahan jaringan atau koneksi. Silakan coba lagi.');
    }
}

/**
 * Step 3: Display the result.
 */
function _showResult(success, message) {
    _showStep('stepResult');

    const icon = document.getElementById('resultIcon');
    const title = document.getElementById('resultTitle');
    const msg = document.getElementById('resultMessage');

    if (success) {
        icon.innerHTML = '<i class="bi bi-check-circle-fill text-success" style="font-size: 4rem"></i>';
        title.textContent = 'Berhasil!';
        title.className = 'fw-bold mt-3 text-success';
    } else {
        icon.innerHTML = '<i class="bi bi-x-circle-fill text-danger" style="font-size: 4rem"></i>';
        title.textContent = 'Gagal';
        title.className = 'fw-bold mt-3 text-danger';
    }
    if (msg) msg.textContent = message;
}

/**
 * Show a specific step and hide others.
 */
function _showStep(stepId) {
    const steps = ['stepGPS', 'stepSubmit', 'stepResult'];
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.toggle('d-none', id !== stepId);
        }
    });
}

// Reload page on modal close if successful
document.addEventListener('DOMContentLoaded', function () {
    const modalEl = document.getElementById('attendanceModal');
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', function () {
            const resultTitle = document.getElementById('resultTitle');
            if (resultTitle && resultTitle.textContent === 'Berhasil!') {
                window.location.reload();
            }
        });
    }
});
