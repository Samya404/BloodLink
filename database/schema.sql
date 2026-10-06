-- ============================================
-- BloodLink Database Schema
-- PostgreSQL
-- ============================================
-- This file is provided as a reference.
-- The actual schema is managed by Flask-Migrate / Alembic.
-- Run: flask db upgrade
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('PATIENT', 'DONOR', 'HOSPITAL', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Donor profiles
CREATE TABLE IF NOT EXISTS donor_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blood_group VARCHAR(5) NOT NULL,
    city VARCHAR(100),
    area VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    availability_status VARCHAR(20) DEFAULT 'AVAILABLE' CHECK (availability_status IN ('AVAILABLE', 'UNAVAILABLE')),
    verification_status VARCHAR(20) DEFAULT 'PENDING' CHECK (verification_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    last_donation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_donor_blood_group ON donor_profiles(blood_group);
CREATE INDEX idx_donor_city ON donor_profiles(city);
CREATE INDEX idx_donor_availability ON donor_profiles(availability_status);

-- Hospitals / Blood Banks
CREATE TABLE IF NOT EXISTS hospitals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'HOSPITAL' CHECK (type IN ('BLOOD_BANK', 'HOSPITAL', 'CLINIC')),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    phone VARCHAR(20),
    email VARCHAR(255),
    verification_status VARCHAR(20) DEFAULT 'PENDING' CHECK (verification_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hospitals_city ON hospitals(city);
CREATE INDEX idx_hospitals_state ON hospitals(state);
CREATE INDEX idx_hospitals_verification ON hospitals(verification_status);

-- Blood Inventory
CREATE TABLE IF NOT EXISTS blood_inventory (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    blood_group VARCHAR(5) NOT NULL,
    component VARCHAR(50) NOT NULL DEFAULT 'WHOLE_BLOOD' CHECK (component IN ('WHOLE_BLOOD', 'PACKED_RED_CELLS', 'PLASMA', 'PLATELETS')),
    available_units INTEGER DEFAULT 0 CHECK (available_units >= 0),
    reserved_units INTEGER DEFAULT 0 CHECK (reserved_units >= 0),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_type VARCHAR(20) DEFAULT 'LOCAL' CHECK (source_type IN ('LOCAL', 'EXTERNAL', 'DEMO')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hospital_id, blood_group, component)
);

CREATE INDEX idx_inventory_blood_group ON blood_inventory(blood_group);
CREATE INDEX idx_inventory_hospital ON blood_inventory(hospital_id);

-- Blood Requests
CREATE TABLE IF NOT EXISTS blood_requests (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hospital_id INTEGER REFERENCES hospitals(id) ON DELETE SET NULL,
    blood_group VARCHAR(5) NOT NULL,
    component VARCHAR(50) DEFAULT 'WHOLE_BLOOD',
    units_required INTEGER NOT NULL CHECK (units_required > 0),
    priority VARCHAR(20) DEFAULT 'NORMAL' CHECK (priority IN ('NORMAL', 'URGENT', 'EMERGENCY')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'MATCHING', 'PARTIALLY_FULFILLED', 'FULFILLED', 'CANCELLED', 'EXPIRED')),
    required_by TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_requests_blood_group ON blood_requests(blood_group);
CREATE INDEX idx_requests_status ON blood_requests(status);
CREATE INDEX idx_requests_created ON blood_requests(created_at);
CREATE INDEX idx_requests_priority ON blood_requests(priority);

-- Donor Matches
CREATE TABLE IF NOT EXISTS donor_matches (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE,
    donor_id INTEGER NOT NULL REFERENCES donor_profiles(id) ON DELETE CASCADE,
    match_score FLOAT,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'NOTIFIED', 'ACCEPTED', 'DECLINED', 'EXPIRED')),
    notified_at TIMESTAMP,
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_matches_request ON donor_matches(request_id);
CREATE INDEX idx_matches_donor ON donor_matches(donor_id);

-- Donations
CREATE TABLE IF NOT EXISTS donations (
    id SERIAL PRIMARY KEY,
    donor_id INTEGER NOT NULL REFERENCES donor_profiles(id) ON DELETE CASCADE,
    donation_date TIMESTAMP,
    blood_group VARCHAR(5),
    component VARCHAR(50),
    collection_location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'COMPLETED' CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_donations_donor ON donations(donor_id);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- API Sources
CREATE TABLE IF NOT EXISTS api_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50),
    enabled BOOLEAN DEFAULT FALSE,
    last_successful_sync TIMESTAMP,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- External Blood Records
CREATE TABLE IF NOT EXISTS external_blood_records (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(100),
    external_record_id VARCHAR(255),
    blood_bank_name VARCHAR(255),
    blood_group VARCHAR(5),
    component VARCHAR(50),
    units_available INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    source_updated_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_external_blood_group ON external_blood_records(blood_group);
CREATE INDEX idx_external_city ON external_blood_records(city);
CREATE INDEX idx_external_provider ON external_blood_records(provider_name);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    description TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
CREATE INDEX idx_audit_action ON audit_logs(action);
