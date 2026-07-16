"""Debug: why admin API returns 403."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from app.extensions import db
from app.models import User

app = create_app('testing')
print("WTF_CSRF_ENABLED:", app.config.get('WTF_CSRF_ENABLED'))
print("TESTING:", app.config.get('TESTING'))

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@pertamina.com', full_name='Admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Test 1: Same context, simple post
    with app.test_client() as c:
        r1 = c.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        print("Login status:", r1.status_code, "contains admin:", b'admin' in r1.data.lower())
        
        r2 = c.post('/api/admin/users/add', json={
            'username': 'dbg2', 'full_name': 'DBG', 'email': 'dbg2@t.com',
            'role': 'mahasiswa', 'password': 'mhs123'
        })
        print("Add user status:", r2.status_code)
        print("Add user body:", r2.data.decode('utf-8', errors='replace')[:300])
        
        # cleanup
        u = User.query.filter_by(username='dbg2').first()
        if u:
            db.session.delete(u)
            db.session.commit()
