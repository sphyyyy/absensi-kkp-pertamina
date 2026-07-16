# Application-wide constants

# User roles
ROLE_MAHASISWA = 'mahasiswa'
ROLE_DOSEN = 'dosen'
ROLE_ADMIN = 'admin'

ALL_ROLES = [ROLE_MAHASISWA, ROLE_DOSEN, ROLE_ADMIN]

# Attendance statuses
STATUS_HADIR = 'hadir'
STATUS_TERLAMBAT = 'terlambat'
STATUS_IZIN = 'izin'
STATUS_ALPHA = 'alpha'

ALL_STATUSES = [STATUS_HADIR, STATUS_TERLAMBAT, STATUS_IZIN, STATUS_ALPHA]

# Attendance types
TYPE_CHECKIN = 'check_in'
TYPE_CHECKOUT = 'check_out'

# Validation error messages
ERR_OUTSIDE_GEOFENCE = 'Anda berada di luar area kantor. Absensi ditolak.'
ERR_OUTSIDE_TIME_WINDOW = 'Saat ini bukan jam absensi yang berlaku.'
ERR_ALREADY_CHECKED_IN = 'Anda sudah melakukan absen masuk hari ini.'
ERR_ALREADY_CHECKED_OUT = 'Anda sudah melakukan absen pulang hari ini.'
ERR_NOT_CHECKED_IN = 'Anda belum melakukan absen masuk hari ini.'
ERR_INVALID_PHOTO = 'Foto yang dikirim tidak valid.'
ERR_PHOTO_REQUIRED = 'Foto selfie wajib disertakan.'
ERR_SESSION_EXPIRED = 'Sesi Anda telah berakhir. Silakan login kembali.'
ERR_UNAUTHORIZED = 'Anda tidak memiliki akses ke halaman ini.'
ERR_GPS_REQUIRED = 'Data lokasi GPS wajib disertakan.'
ERR_GPS_LOW_ACCURACY = 'Akurasi GPS terlalu rendah. Mohon coba di area terbuka.'

# Success messages
MSG_CHECKIN_SUCCESS = 'Absen masuk berhasil dicatat.'
MSG_CHECKOUT_SUCCESS = 'Absen pulang berhasil dicatat.'
MSG_LOGIN_SUCCESS = 'Login berhasil. Selamat datang!'
MSG_LOGOUT_SUCCESS = 'Anda telah berhasil logout.'

# GPS
MAX_GPS_ACCURACY_METERS = 250  # Default 250m accuracy threshold (configurable via Admin)
