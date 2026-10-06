-- ============================================
-- BloodLink — Demo Seed Data
-- ============================================
-- This file creates demo accounts and sample data for development/testing.
-- All data is fictional and clearly labeled.
-- Passwords are bcrypt hashes of 'Password123!' (for demo only).
-- ============================================

-- NOTE: When using Flask-Migrate, seed data is inserted via the
-- `flask seed` CLI command (see backend/app.py).
-- This SQL file is provided as a reference and for direct DB seeding.

-- ============================================
-- DEMO USERS
-- ============================================
-- Password for all demo accounts: Password123!
-- The hash below is for 'Password123!' using werkzeug.security.generate_password_hash

-- Admin User
INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('Admin User', 'admin@bloodlink.demo', '+91-9000000001',
        'pbkdf2:sha256:600000$placeholder$hash', 'ADMIN', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Donor User
INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('Rahul Sharma', 'donor@bloodlink.demo', '+91-9000000002',
        'pbkdf2:sha256:600000$placeholder$hash', 'DONOR', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Patient User
INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('Priya Patel', 'patient@bloodlink.demo', '+91-9000000003',
        'pbkdf2:sha256:600000$placeholder$hash', 'PATIENT', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Hospital User
INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('City Hospital Admin', 'hospital@bloodlink.demo', '+91-9000000004',
        'pbkdf2:sha256:600000$placeholder$hash', 'HOSPITAL', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Additional Donors
INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('Amit Kumar', 'donor2@bloodlink.demo', '+91-9000000005',
        'pbkdf2:sha256:600000$placeholder$hash', 'DONOR', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
VALUES ('Sneha Roy', 'donor3@bloodlink.demo', '+91-9000000006',
        'pbkdf2:sha256:600000$placeholder$hash', 'DONOR', TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- DEMO DONOR PROFILES
-- ============================================
-- Note: Actual seeding uses the flask seed command which creates proper password hashes.
-- These SQL inserts reference user IDs that depend on insertion order.

-- Rahul Sharma - O+ Donor in Kolkata
INSERT INTO donor_profiles (user_id, blood_group, city, area, latitude, longitude, availability_status, verification_status)
SELECT id, 'O+', 'Kolkata', 'Salt Lake', 22.57, 88.41, 'AVAILABLE', 'VERIFIED'
FROM users WHERE email = 'donor@bloodlink.demo'
ON CONFLICT (user_id) DO NOTHING;

-- Amit Kumar - B+ Donor in Delhi
INSERT INTO donor_profiles (user_id, blood_group, city, area, latitude, longitude, availability_status, verification_status)
SELECT id, 'B+', 'Delhi', 'Connaught Place', 28.63, 77.22, 'AVAILABLE', 'VERIFIED'
FROM users WHERE email = 'donor2@bloodlink.demo'
ON CONFLICT (user_id) DO NOTHING;

-- Sneha Roy - A- Donor in Mumbai
INSERT INTO donor_profiles (user_id, blood_group, city, area, latitude, longitude, availability_status, verification_status)
SELECT id, 'A-', 'Mumbai', 'Andheri', 19.12, 72.85, 'AVAILABLE', 'PENDING'
FROM users WHERE email = 'donor3@bloodlink.demo'
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- DEMO HOSPITALS
-- ============================================
-- These are fictional hospitals for demo purposes.

INSERT INTO hospitals (user_id, name, type, address, city, state, latitude, longitude, phone, email, verification_status)
SELECT id, 'City Demo Hospital', 'HOSPITAL',
       '123 Demo Medical Road', 'Kolkata', 'West Bengal',
       22.5726, 88.3639, '+91-33-1234567', 'cityhospital@demo.bloodlink',
       'VERIFIED'
FROM users WHERE email = 'hospital@bloodlink.demo'
ON CONFLICT DO NOTHING;

INSERT INTO hospitals (name, type, address, city, state, latitude, longitude, phone, email, verification_status)
VALUES ('Metro Demo Blood Bank', 'BLOOD_BANK',
        '456 Demo Health Avenue', 'Delhi', 'Delhi',
        28.6139, 77.2090, '+91-11-2345678', 'metrobb@demo.bloodlink',
        'VERIFIED')
ON CONFLICT DO NOTHING;

INSERT INTO hospitals (name, type, address, city, state, latitude, longitude, phone, email, verification_status)
VALUES ('Central Demo Hospital', 'HOSPITAL',
        '789 Demo Care Street', 'Mumbai', 'Maharashtra',
        19.0760, 72.8777, '+91-22-3456789', 'centralhosp@demo.bloodlink',
        'VERIFIED')
ON CONFLICT DO NOTHING;

INSERT INTO hospitals (name, type, address, city, state, latitude, longitude, phone, email, verification_status)
VALUES ('South Demo Blood Centre', 'BLOOD_BANK',
        '321 Demo Wellness Road', 'Bengaluru', 'Karnataka',
        12.9716, 77.5946, '+91-80-4567890', 'southbb@demo.bloodlink',
        'PENDING')
ON CONFLICT DO NOTHING;

-- ============================================
-- DEMO BLOOD INVENTORY
-- ============================================
-- All inventory is marked as DEMO source_type.

-- City Demo Hospital - Kolkata
INSERT INTO blood_inventory (hospital_id, blood_group, component, available_units, reserved_units, source_type)
SELECT h.id, bg.group, 'WHOLE_BLOOD', bg.units, 0, 'DEMO'
FROM hospitals h
CROSS JOIN (
    VALUES ('A+', 12), ('A-', 4), ('B+', 8), ('B-', 3),
           ('AB+', 5), ('AB-', 2), ('O+', 15), ('O-', 6)
) AS bg(group, units)
WHERE h.name = 'City Demo Hospital'
ON CONFLICT DO NOTHING;

-- Metro Demo Blood Bank - Delhi
INSERT INTO blood_inventory (hospital_id, blood_group, component, available_units, reserved_units, source_type)
SELECT h.id, bg.group, 'WHOLE_BLOOD', bg.units, 0, 'DEMO'
FROM hospitals h
CROSS JOIN (
    VALUES ('A+', 20), ('A-', 7), ('B+', 15), ('B-', 5),
           ('AB+', 8), ('AB-', 3), ('O+', 25), ('O-', 10)
) AS bg(group, units)
WHERE h.name = 'Metro Demo Blood Bank'
ON CONFLICT DO NOTHING;

-- Central Demo Hospital - Mumbai
INSERT INTO blood_inventory (hospital_id, blood_group, component, available_units, reserved_units, source_type)
SELECT h.id, bg.group, 'WHOLE_BLOOD', bg.units, 0, 'DEMO'
FROM hospitals h
CROSS JOIN (
    VALUES ('A+', 18), ('A-', 6), ('B+', 10), ('B-', 4),
           ('AB+', 7), ('AB-', 2), ('O+', 22), ('O-', 8)
) AS bg(group, units)
WHERE h.name = 'Central Demo Hospital'
ON CONFLICT DO NOTHING;

-- ============================================
-- DEMO BLOOD REQUESTS
-- ============================================

INSERT INTO blood_requests (requester_id, hospital_id, blood_group, component, units_required, priority, status, notes)
SELECT u.id, h.id, 'B+', 'WHOLE_BLOOD', 3, 'URGENT', 'PENDING',
       'Demo request - Urgent need for surgery'
FROM users u, hospitals h
WHERE u.email = 'patient@bloodlink.demo' AND h.name = 'City Demo Hospital'
ON CONFLICT DO NOTHING;

INSERT INTO blood_requests (requester_id, blood_group, component, units_required, priority, status, notes)
SELECT u.id, 'O-', 'PACKED_RED_CELLS', 2, 'EMERGENCY', 'MATCHING',
       'Demo request - Emergency trauma case'
FROM users u
WHERE u.email = 'patient@bloodlink.demo'
ON CONFLICT DO NOTHING;

-- ============================================
-- DEMO API SOURCE
-- ============================================

INSERT INTO api_sources (name, source_type, enabled)
VALUES ('MockBloodProvider', 'MOCK', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- NOTE
-- ============================================
-- This seed data uses placeholder password hashes.
-- For working demo accounts, use the Flask CLI:
--   flask seed
-- This will create properly hashed passwords.
