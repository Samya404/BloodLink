import pytest

def test_add_inventory(client, db, hospital_headers):
    """Hospital adds inventory, check 201"""
    response = client.post('/api/v1/inventory/', headers=hospital_headers, json={
        'blood_group': 'O+',
        'units': 5
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['units'] == 5
    assert data['data']['blood_group'] == 'O+'

def test_update_inventory(client, db, hospital_headers):
    """Update units, check changed"""
    client.post('/api/v1/inventory/', headers=hospital_headers, json={
        'blood_group': 'A+',
        'units': 2
    })
    
    response = client.patch('/api/v1/inventory/', headers=hospital_headers, json={
        'blood_group': 'A+',
        'units': 10
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['units'] == 10

def test_prevent_negative_inventory(client, db, hospital_headers):
    """Try setting units to -1, check 400"""
    response = client.post('/api/v1/inventory/', headers=hospital_headers, json={
        'blood_group': 'B+',
        'units': -1
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False

def test_inventory_audit_log(client, db, hospital_headers):
    """Update inventory, check audit log created"""
    client.post('/api/v1/inventory/', headers=hospital_headers, json={
        'blood_group': 'AB+',
        'units': 5
    })
    
    response = client.get('/api/v1/inventory/audit', headers=hospital_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) > 0

def test_patient_cannot_modify_inventory(client, db, auth_headers):
    """Patient tries POST /inventory, check 403"""
    response = client.post('/api/v1/inventory/', headers=auth_headers, json={
        'blood_group': 'O+',
        'units': 5
    })
    assert response.status_code == 403

def test_donor_cannot_access_admin(client, db, donor_headers):
    """Donor tries GET /admin/statistics, check 403"""
    response = client.get('/api/v1/admin/statistics', headers=donor_headers)
    assert response.status_code == 403

def test_hospital_cannot_access_admin(client, db, hospital_headers):
    """Hospital tries GET /admin/users, check 403"""
    response = client.get('/api/v1/admin/users', headers=hospital_headers)
    assert response.status_code == 403
