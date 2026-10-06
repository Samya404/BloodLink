import pytest

def test_register_patient_success(client, db):
    """Register patient, check 201, check user data returned"""
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'New Patient',
        'email': 'newpatient@test.com',
        'password': 'TestPass123!',
        'phone': '9876543210',
        'role': 'PATIENT'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['user']['email'] == 'newpatient@test.com'
    assert data['data']['user']['role'] == 'PATIENT'

def test_register_donor_success(client, db):
    """Register donor with donor_data, check profile created"""
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'New Donor',
        'email': 'newdonor@test.com',
        'password': 'TestPass123!',
        'phone': '9876543211',
        'role': 'DONOR',
        'donor_data': {
            'blood_group': 'A+',
            'city': 'Delhi',
            'area': 'CP'
        }
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['user']['donor_profile'] is not None
    assert data['data']['user']['donor_profile']['blood_group'] == 'A+'

def test_register_hospital_success(client, db):
    """Register hospital with hospital_data, check hospital created"""
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'New Hospital',
        'email': 'newhosp@test.com',
        'password': 'TestPass123!',
        'phone': '9876543212',
        'role': 'HOSPITAL',
        'hospital_data': {
            'name': 'City Care',
            'type': 'HOSPITAL',
            'address': 'Main St',
            'city': 'Delhi',
            'state': 'Delhi'
        }
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['user']['hospital_profile'] is not None
    assert data['data']['user']['hospital_profile']['name'] == 'City Care'

def test_register_duplicate_email(client, db):
    """Try registering same email twice, check 409/400"""
    client.post('/api/v1/auth/register', json={
        'full_name': 'Patient1',
        'email': 'dup@test.com',
        'password': 'TestPass123!',
        'phone': '9876543210',
        'role': 'PATIENT'
    })
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'Patient2',
        'email': 'dup@test.com',
        'password': 'TestPass123!',
        'phone': '9876543213',
        'role': 'PATIENT'
    })
    assert response.status_code in [400, 409]
    assert response.get_json()['success'] is False

def test_register_invalid_email(client, db):
    """Invalid email format, check 400"""
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'Patient',
        'email': 'invalid-email',
        'password': 'TestPass123!',
        'phone': '9876543210',
        'role': 'PATIENT'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_register_short_password(client, db):
    """Password < 8 chars, check 400"""
    response = client.post('/api/v1/auth/register', json={
        'full_name': 'Patient',
        'email': 'shortpass@test.com',
        'password': 'short',
        'phone': '9876543210',
        'role': 'PATIENT'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_register_missing_fields(client, db):
    """Missing required fields, check 400"""
    response = client.post('/api/v1/auth/register', json={
        'email': 'missing@test.com',
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_login_success(client, db, auth_headers):
    """Login with valid credentials, check tokens returned"""
    response = client.post('/api/v1/auth/login', json={
        'email': 'testpatient@test.com',
        'password': 'TestPass123!'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']

def test_login_wrong_password(client, db, auth_headers):
    """Wrong password, check 401"""
    response = client.post('/api/v1/auth/login', json={
        'email': 'testpatient@test.com',
        'password': 'WrongPassword123!'
    })
    assert response.status_code == 401
    assert response.get_json()['success'] is False

def test_login_nonexistent_email(client, db):
    """Email not found, check 401"""
    response = client.post('/api/v1/auth/login', json={
        'email': 'notfound@test.com',
        'password': 'TestPass123!'
    })
    assert response.status_code == 401
    assert response.get_json()['success'] is False

def test_get_me_authenticated(client, db, auth_headers):
    """GET /auth/me with valid token, check user data"""
    response = client.get('/api/v1/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['email'] == 'testpatient@test.com'

def test_get_me_unauthenticated(client, db):
    """GET /auth/me without token, check 401"""
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401
    assert response.get_json()['success'] is False

def test_refresh_token(client, db):
    """POST /auth/refresh with refresh token, check new access token"""
    client.post('/api/v1/auth/register', json={
        'full_name': 'Refresh User',
        'email': 'refresh@test.com',
        'password': 'TestPass123!',
        'phone': '9876543220',
        'role': 'PATIENT'
    })
    login_resp = client.post('/api/v1/auth/login', json={
        'email': 'refresh@test.com',
        'password': 'TestPass123!'
    })
    tokens = login_resp.get_json()['data']
    refresh_token = tokens['refresh_token']
    
    response = client.post(
        '/api/v1/auth/refresh',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data['data']
