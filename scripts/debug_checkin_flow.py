import requests
import re

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def get_csrf_and_login(username, password):
    r0 = session.get(f"{BASE_URL}/auth/login")
    match_csrf = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', r0.text)
    csrf_token = match_csrf.group(1) if match_csrf else ""
    
    r = session.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password,
        "csrf_token": csrf_token
    })
    
    alerts = re.findall(r'<div class="alert[^>]*>(.*?)</div>', r.text, re.DOTALL)
    alerts_clean = [re.sub(r'<[^>]+>', '', a).strip() for a in alerts]
    return r.status_code, r.url, alerts_clean, csrf_token

# 1. Login as admin
print("--- Step 1: Login Admin ---", flush=True)
status, url, alerts, csrf = get_csrf_and_login("admin", "admin123")
print(f"Status: {status}, URL: {url}, Alerts: {alerts}", flush=True)

# 2. Check current settings via /dashboard/admin
print("--- Step 2: Check Admin Dashboard Settings ---", flush=True)
r_admin = session.get(f"{BASE_URL}/dashboard/admin")
match_meta = re.search(r'name="csrf-token"\s+content="([^"]+)"', r_admin.text)
csrf_token = match_meta.group(1) if match_meta else csrf

start_curr = re.search(r'name="CHECKIN_START"\s+value="([^"]+)"', r_admin.text)
end_curr = re.search(r'name="CHECKIN_END"\s+value="([^"]+)"', r_admin.text)
print(f"Current values in dashboard: CHECKIN_START={start_curr.group(1) if start_curr else 'N/A'}, CHECKIN_END={end_curr.group(1) if end_curr else 'N/A'}", flush=True)

# 3. Update CHECKIN_END to 23:00 via API
print("--- Step 3: Update CHECKIN_END to 23:00 via API ---", flush=True)
headers = {"X-CSRFToken": csrf_token, "Content-Type": "application/json"}
payload = {
    "GEOFENCE_LAT": "-5.1477",
    "GEOFENCE_LNG": "119.4327",
    "GEOFENCE_RADIUS": "100",
    "MAX_GPS_ACCURACY": "250",
    "CHECKIN_START": "07:00",
    "CHECKIN_END": "23:00",
    "CHECKOUT_START": "16:00",
    "CHECKOUT_END": "18:00"
}
r_update = session.post(f"{BASE_URL}/api/admin/settings/update", json=payload, headers=headers)
print(f"Status: {r_update.status_code}, JSON: {r_update.text[:150]}", flush=True)

# 4. Check what setting is actually saved right now
print("--- Step 4: Check Dashboard Settings After Update ---", flush=True)
r_settings = session.get(f"{BASE_URL}/dashboard/admin")
end_match = re.search(r'name="CHECKIN_END"\s+value="([^"]+)"', r_settings.text)
print(f"CHECKIN_END value after save: {end_match.group(1) if end_match else 'NOT FOUND'}", flush=True)

# 5. Logout
session.get(f"{BASE_URL}/auth/logout")

# 6. Login as mahasiswa (2361008)
print("--- Step 5: Login Mahasiswa (2361008) ---", flush=True)
status_m, url_m, alerts_m, csrf_m = get_csrf_and_login("2361008", "mhs123")
print(f"Status: {status_m}, URL: {url_m}, Alerts: {alerts_m}", flush=True)

# 7. Check status via API
print("--- Step 6: Check Attendance Status API ---", flush=True)
r_status = session.get(f"{BASE_URL}/attendance/status")
print(f"Status API response: {r_status.status_code}, JSON: {r_status.text[:150]}", flush=True)

# 8. Attempt Check-In
print("--- Step 7: Attempt Check-In ---", flush=True)
r_mhs_dash = session.get(f"{BASE_URL}/dashboard/")
match_mhs_meta = re.search(r'name="csrf-token"\s+content="([^"]+)"', r_mhs_dash.text)
csrf_mhs = match_mhs_meta.group(1) if match_mhs_meta else csrf_m
headers_mhs = {"X-CSRFToken": csrf_mhs, "Content-Type": "application/json"}

checkin_payload = {
    "latitude": -5.1477,
    "longitude": 119.4327,
    "accuracy": 15,
    "photo": None
}
r_checkin = session.post(f"{BASE_URL}/attendance/check-in", json=checkin_payload, headers=headers_mhs)
print(f"Check-in status: {r_checkin.status_code}, JSON: {r_checkin.text[:200]}", flush=True)
