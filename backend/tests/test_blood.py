import pytest

def test_get_blood_groups(client, db):
    """GET /blood/groups, check all 8 groups returned"""
    response = client.get('/api/v1/blood/groups')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 8
    assert 'A+' in data['data']

def test_search_availability_no_filters(client, db):
    """GET /blood/availability, check 200"""
    response = client.get('/api/v1/blood/availability')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)

def test_search_availability_by_blood_group(client, db, donor_headers):
    """GET /blood/availability?blood_group=B+, check filtered"""
    response = client.get('/api/v1/blood/availability?blood_group=O+')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_search_availability_by_city(client, db, donor_headers):
    """GET /blood/availability?city=Kolkata, check filtered"""
    response = client.get('/api/v1/blood/availability?city=Kolkata')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_search_availability_empty_result(client, db):
    """Search for non-existent combo, check empty array"""
    response = client.get('/api/v1/blood/availability?city=NonExistentCity123')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) == 0

def test_search_availability_invalid_blood_group(client, db):
    """Invalid blood group, check 400"""
    response = client.get('/api/v1/blood/availability?blood_group=XYZ')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
