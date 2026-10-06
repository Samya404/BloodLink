import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from extensions import db as _db

@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    """Create clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        # Clean all tables
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Register and login a test user, return auth headers."""
    # Register
    client.post('/api/v1/auth/register', json={
        'full_name': 'Test Patient',
        'email': 'testpatient@test.com',
        'password': 'TestPass123!',
        'phone': '1234567890',
        'role': 'PATIENT'
    })
    # Login
    response = client.post('/api/v1/auth/login', json={
        'email': 'testpatient@test.com',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

@pytest.fixture
def donor_headers(client):
    """Register and login a donor user."""
    client.post('/api/v1/auth/register', json={
        'full_name': 'Test Donor',
        'email': 'testdonor@test.com',
        'password': 'TestPass123!',
        'phone': '1234567891',
        'role': 'DONOR',
        'donor_data': {
            'blood_group': 'O+',
            'city': 'Kolkata',
            'area': 'Salt Lake'
        }
    })
    response = client.post('/api/v1/auth/login', json={
        'email': 'testdonor@test.com',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

@pytest.fixture
def hospital_headers(client):
    """Register and login a hospital user."""
    client.post('/api/v1/auth/register', json={
        'full_name': 'Test Hospital Admin',
        'email': 'testhospital@test.com',
        'password': 'TestPass123!',
        'phone': '1234567892',
        'role': 'HOSPITAL',
        'hospital_data': {
            'name': 'Test Hospital',
            'type': 'HOSPITAL',
            'address': '123 Test St',
            'city': 'Kolkata',
            'state': 'West Bengal'
        }
    })
    response = client.post('/api/v1/auth/login', json={
        'email': 'testhospital@test.com',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

@pytest.fixture
def admin_headers(client, db):
    """Create admin user and return auth headers."""
    from models.user import User
    admin = User(
        full_name='Test Admin',
        email='testadmin@test.com',
        phone='1234567899',
        role='ADMIN',
        is_active=True
    )
    admin.set_password('TestPass123!')
    db.session.add(admin)
    db.session.commit()
    
    response = client.post('/api/v1/auth/login', json={
        'email': 'testadmin@test.com',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
