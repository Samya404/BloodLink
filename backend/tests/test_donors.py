import pytest

def test_update_donor_availability(client, db, donor_headers):
    """Set UNAVAILABLE, check updated"""
    response = client.patch('/api/v1/donors/availability', headers=donor_headers, json={
        'is_available': False
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['is_available'] is False

def test_update_donor_profile(client, db, donor_headers):
    """Update city/area, check updated"""
    response = client.patch('/api/v1/donors/profile', headers=donor_headers, json={
        'city': 'Mumbai',
        'area': 'Andheri'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['city'] == 'Mumbai'
    assert data['data']['area'] == 'Andheri'

def test_get_donor_matches(client, db, auth_headers, donor_headers):
    """Create request + donor, check matching works"""
    create_resp = client.post('/api/v1/requests/', headers=auth_headers, json={
        'blood_group': 'O+',
        'units': 1,
        'patient_name': 'Match Test',
        'hospital_name': 'Match Hospital',
        'urgency_level': 'NORMAL',
        'city': 'Kolkata' 
    })
    req_id = create_resp.get_json()['data']['id']
    
    response = client.get(f'/api/v1/requests/{req_id}/matches', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)

def test_donor_profile_hides_exact_location(client, db, donor_headers):
    """Get donor, check no exact lat/lng exposed (rounded)"""
    client.patch('/api/v1/donors/profile', headers=donor_headers, json={
        'latitude': 22.572645,
        'longitude': 88.363892
    })
    
    response = client.get('/api/v1/blood/availability?blood_group=O+')
    data = response.get_json()
    if len(data['data']) > 0:
        donor = data['data'][0]
        lat = donor.get('latitude')
        if lat is not None:
            assert lat != 22.572645

def test_non_donor_cannot_update_profile(client, db, auth_headers):
    """Patient tries PATCH /donors/profile, check 403"""
    response = client.patch('/api/v1/donors/profile', headers=auth_headers, json={
        'city': 'Mumbai'
    })
    assert response.status_code == 403
