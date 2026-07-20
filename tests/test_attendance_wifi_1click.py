import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.extensions import db
from app.models import User, Setting, Attendance
from app.utils.constants import STATUS_HADIR

class Test1ClickAttendanceWifi(unittest.TestCase):
    def setUp(self):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test student
        self.user = User(
            username='mhs_wifi',
            email='mhs_wifi@test.com',
            full_name='Mahasiswa WiFi Test',
            role='mahasiswa',
            nim='20261001',
            is_active=True
        )
        self.user.set_password('mhs123')
        db.session.add(self.user)
        db.session.commit()

        # Set default geofence to Makassar Pertamina or local center
        Setting.set('GEOFENCE_LAT', '-5.1477')
        Setting.set('GEOFENCE_LNG', '119.4327')
        Setting.set('GEOFENCE_RADIUS', '500')
        Setting.set('CHECKIN_START', '00:00')
        Setting.set('CHECKIN_END', '23:59')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_1click_checkin_without_photo(self):
        """Verify 1-Click Check-In works without a photo when Wi-Fi check is disabled."""
        self.client.post('/auth/login', data={'username': 'mhs_wifi', 'password': 'mhs123'}, follow_redirects=True)
        
        # Disable wifi check
        Setting.set('ENABLE_WIFI_VALIDATION', 'false')

        payload = {
            'latitude': -5.1477,
            'longitude': 119.4327,
            'accuracy': 10,
            'photo': None  # No selfie sent!
        }
        res = self.client.post('/attendance/check-in', json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 200, f"Check-in failed: {data}")
        self.assertTrue(data['success'])
        
        # Check database record
        att = Attendance.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(att)
        self.assertEqual(att.photo_in, '1-click-geofence')
        print(" -> [TEST 1 PASSED] 1-Click Check-In without selfie succeeded!")

    def test_02_outside_geofence_rejection(self):
        """Verify check-in is rejected when location is outside the GPS geofence radius."""
        self.client.post('/auth/login', data={'username': 'mhs_wifi', 'password': 'mhs123'}, follow_redirects=True)

        # Send coordinates far outside office geofence (-5.1477, 119.4327)
        payload = {
            'latitude': -6.2000,
            'longitude': 106.8166,
            'accuracy': 10,
            'photo': None
        }
        res = self.client.post('/attendance/check-in', json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn("Anda berada di luar area kantor", data['message'])
        print(" -> [TEST 2 PASSED] Outside GPS geofence properly rejected attendance!")

    def test_03_inside_geofence_acceptance(self):
        """Verify check-in succeeds cleanly when inside GPS geofence radius without Wi-Fi check."""
        self.client.post('/auth/login', data={'username': 'mhs_wifi', 'password': 'mhs123'}, follow_redirects=True)

        payload = {
            'latitude': -5.1477,
            'longitude': 119.4327,
            'accuracy': 10,
            'photo': None
        }
        res = self.client.post('/attendance/check-in', json=payload)
        data = res.get_json()
        self.assertEqual(res.status_code, 200, f"Expected success but got: {data}")
        self.assertTrue(data['success'])
        print(" -> [TEST 3 PASSED] Inside GPS geofence accepted attendance cleanly!")

if __name__ == '__main__':
    unittest.main()
