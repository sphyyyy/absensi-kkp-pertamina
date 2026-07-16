/**
 * Camera module for the KKP Attendance System.
 * Handles camera access, selfie capture, and photo preview.
 */

const Camera = {
    stream: null,
    photoData: null,

    /**
     * Start the camera and display preview in the video element.
     * @param {HTMLVideoElement} videoEl - The <video> element for preview.
     * @returns {Promise<void>}
     */
    async start(videoEl) {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                },
                audio: false,
            });
            videoEl.srcObject = this.stream;
            await videoEl.play();
        } catch (err) {
            let message = 'Gagal mengakses kamera.';
            if (err.name === 'NotAllowedError') {
                message = 'Izin kamera ditolak. Izinkan akses kamera pada browser.';
            } else if (err.name === 'NotFoundError') {
                message = 'Kamera tidak ditemukan pada perangkat ini.';
            }
            throw new Error(message);
        }
    },

    /**
     * Capture a photo from the video stream.
     * @param {HTMLVideoElement} videoEl - The <video> element.
     * @param {HTMLCanvasElement} canvasEl - The <canvas> element for capture.
     * @returns {string} Base64-encoded JPEG image data (without prefix).
     */
    capture(videoEl, canvasEl) {
        canvasEl.width = videoEl.videoWidth;
        canvasEl.height = videoEl.videoHeight;

        const ctx = canvasEl.getContext('2d');

        // Mirror the image (selfie mode)
        ctx.translate(canvasEl.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(videoEl, 0, 0);
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        // Convert to base64 JPEG
        const dataUrl = canvasEl.toDataURL('image/jpeg', 0.85);
        this.photoData = dataUrl.split(',')[1]; // Remove "data:image/jpeg;base64," prefix

        return this.photoData;
    },

    /**
     * Stop the camera stream and release resources.
     */
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    },

    /**
     * Reset captured photo data.
     */
    reset() {
        this.photoData = null;
    },
};
