import pytest

def test_create_request_success(client, db, auth_headers):
    """Create request with valid data, check 201"""
    response = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'B+',
        'units': 2,
        'patient_name': 'John Doe',
        'hospital_name': 'General Hospital',
        'urgency_level': 'HIGH',
        'city': 'Mumbai'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['blood_group'] == 'B+'
    assert data['data']['units'] == 2

def test_create_request_invalid_blood_group(client, db, auth_headers):
    """Invalid blood group, check 400"""
    response = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'XYZ',
        'units': 2,
        'patient_name': 'John Doe',
        'hospital_name': 'General Hospital',
        'urgency_level': 'HIGH',
        'city': 'Mumbai'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_create_request_invalid_units_zero(client, db, auth_headers):
    """units=0, check 400"""
    response = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'A+',
        'units': 0,
        'patient_name': 'John Doe',
        'hospital_name': 'General Hospital',
        'urgency_level': 'HIGH',
        'city': 'Mumbai'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_create_request_invalid_units_negative(client, db, auth_headers):
    """units=-1, check 400"""
    response = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'A+',
        'units': -1,
        'patient_name': 'John Doe',
        'hospital_name': 'General Hospital',
        'urgency_level': 'HIGH',
        'city': 'Mumbai'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_create_request_unauthenticated(client, db):
    """No token, check 401"""
    response = client.post('/api/v1/requests/', json={
        'blood_group': 'B+',
        'units': 2,
        'patient_name': 'John Doe',
        'hospital_name': 'General Hospital',
        'urgency_level': 'HIGH',
        'city': 'Mumbai'
    })
    assert response.status_code == 401
    assert response.get_json()['success'] is False

def test_get_own_requests(client, db, auth_headers):
    """Create request then list, check own request appears"""
    client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'AB+',
        'units': 1,
        'patient_name': 'Own Req Test',
        'hospital_name': 'General Hospital',
        'urgency_level': 'NORMAL',
        'city': 'Mumbai'
    })
    response = client.get('/api/v1/requests/my', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) >= 1
    assert any(req['patient_name'] == 'Own Req Test' for req in data['data'])

def test_get_request_detail(client, db, auth_headers):
    """Create then GET by id, check all fields"""
    create_resp = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'O-',
        'units': 3,
        'patient_name': 'Detail Test',
        'hospital_name': 'Detail Hospital',
        'urgency_level': 'CRITICAL',
        'city': 'Chennai'
    })
    req_id = create_resp.get_json()['data']['id']
    
    response = client.get(f'/api/v1/requests/{req_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['blood_group'] == 'O-'
    assert data['data']['units'] == 3
    assert data['data']['patient_name'] == 'Detail Test'

def test_cancel_request(client, db, auth_headers):
    """Create then cancel, check status=CANCELLED"""
    create_resp = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'A-',
        'units': 1,
        'patient_name': 'Cancel Test',
        'hospital_name': 'Cancel Hospital',
        'urgency_level': 'NORMAL',
        'city': 'Pune'
    })
    req_id = create_resp.get_json()['data']['id']
    
    response = client.patch(f'/api/v1/requests/{req_id}/status', headers=auth_headers, json={
        'status': 'CANCELLED'
    })
    assert response.status_code == 200
    assert response.get_json()['data']['status'] == 'CANCELLED'

def test_cancel_others_request(client, db, auth_headers, donor_headers):
    """Try cancelling another user's request, check 403"""
    create_resp = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'A-',
        'units': 1,
        'patient_name': 'Other Cancel Test',
        'hospital_name': 'Cancel Hospital',
        'urgency_level': 'NORMAL',
        'city': 'Pune'
    })
    req_id = create_resp.get_json()['data']['id']
    
    response = client.patch(f'/api/v1/requests/{req_id}/status', headers=donor_headers, json={
        'status': 'CANCELLED'
    })
    assert response.status_code == 403

def test_update_request_status(client, db, auth_headers, admin_headers):
    """HOSPITAL/ADMIN updates status, check changed"""
    create_resp = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'B-',
        'units': 2,
        'patient_name': 'Status Test',
        'hospital_name': 'Status Hospital',
        'urgency_level': 'NORMAL',
        'city': 'Pune'
    })
    req_id = create_resp.get_json()['data']['id']
    
    response = client.patch(f'/api/v1/requests/{req_id}/status', headers=admin_headers, json={
        'status': 'FULFILLED'
    })
    assert response.status_code == 200
    assert response.get_json()['data']['status'] == 'FULFILLED'
