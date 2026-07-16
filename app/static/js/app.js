/**
 * Main application JavaScript for the KKP Attendance System.
 * Handles CSRF tokens for AJAX, flash message auto-dismiss, and global utilities.
 */

(function () {
    'use strict';

    // ── CSRF Token Setup ──
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

    /**
     * Make a fetch request with CSRF token and JSON body.
     * @param {string} url - The endpoint URL.
     * @param {object} data - The JSON body.
     * @returns {Promise<object>} Parsed JSON response.
     */
    window.apiFetch = async function (url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data),
        });
        return response.json();
    };

    // ── Auto-dismiss flash messages ──
    document.addEventListener('DOMContentLoaded', function () {
        const alerts = document.querySelectorAll('.flash-alert');
        alerts.forEach((alert) => {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, 5000);
        });
    });

    // ── Toast notification utility ──
    window.showToast = function (message, type = 'info') {
        const container = document.getElementById('flashContainer');
        if (!container) return;

        const iconMap = {
            success: 'check-circle-fill',
            danger: 'x-circle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill',
        };

        const html = `
            <div class="alert alert-${type} alert-dismissible fade show flash-alert" role="alert">
                <div class="d-flex align-items-center gap-2">
                    <i class="bi bi-${iconMap[type] || 'info-circle-fill'}"></i>
                    <span>${message}</span>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);

        // Auto-dismiss after 5 seconds
        const newAlert = container.lastElementChild;
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(newAlert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    };
})();
