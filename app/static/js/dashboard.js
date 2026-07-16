/**
 * Dashboard attendance flow controller for the KKP Attendance System.
 * Orchestrates the multi-step attendance process: GPS → Camera → Submit → Result.
 */

let currentAttendanceType = null;
let gpsData = null;

/**
 * Start the attendance flow (called by the action button).
 * @param {string} type - 'check_in' or 'check_out'
 */
function startAttendance(type) {
    currentAttendanceType = type;
    gpsData = null;
    Camera.reset();

    // Update modal title
    const title = type === 'check_in' ? 'Absen Masuk' : 'Absen Pulang';
    document.getElementById('attendanceModalTitle').textContent = title;

    // Reset all steps
    _showStep('stepGPS');
    document.getElementById('gpsInfo').classList.add('d-none');
    document.getElementById('gpsError').classList.add('d-none');

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('attendanceModal'));
    modal.show();

    // Start GPS acquisition
    _acquireGPS();
}

/**
 * Step 1: Acquire GPS position.
 */
async function _acquireGPS() {
    try {
        gpsData = await GeoLocation.getCurrentPosition();

        // Display GPS info
        document.getElementById('gpsLat').textContent = gpsData.latitude.toFixed(6);
        document.getElementById('gpsLng').textContent = gpsData.longitude.toFixed(6);
        document.getElementById('gpsAcc').textContent = gpsData.accuracy.toFixed(0) + ' m';
        document.getElementById('gpsInfo').classList.remove('d-none');

        // Move directly to submit step (1-Click Geofence & Wi-Fi Mode!)
        setTimeout(() => {
            _submitAttendance();
        }, 800);

    } catch (err) {
        document.getElementById('gpsError').textContent = err.message;
        document.getElementById('gpsError').classList.remove('d-none');
    }
}

/**
 * Step 2: Start camera preview (Deprecated / Unused in 1-Click Geofence Mode).
 */
async function _startCamera() {}

/**
 * Capture a selfie photo (Deprecated / Unused).
 */
function capturePhoto() {}

/**
 * Retake the selfie photo (Deprecated / Unused).
 */
function retakePhoto() {}

/**
 * Step 3: Submit attendance data to the server (1-Click Geofence & Wi-Fi Check).
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
        photo: null,
    };

    try {
        const result = await apiFetch(endpoint, payload);
        _showResult(result.success, result.message);
    } catch (err) {
        _showResult(false, 'Terjadi kesalahan jaringan atau koneksi. Silakan coba lagi.');
    }
}

/**
 * Step 4: Display the result.
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
    msg.textContent = message;
}

/**
 * Show a specific step and hide others.
 */
function _showStep(stepId) {
    const steps = ['stepGPS', 'stepCamera', 'stepSubmit', 'stepResult'];
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.toggle('d-none', id !== stepId);
        }
    });
}

// Clean up camera when modal closes
document.addEventListener('DOMContentLoaded', function () {
    const modalEl = document.getElementById('attendanceModal');
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', function () {
            Camera.stop();
            // Reload page if attendance was successful
            const resultTitle = document.getElementById('resultTitle');
            if (resultTitle && resultTitle.textContent === 'Berhasil!') {
                window.location.reload();
            }
        });
    }
});
