# BloodLink — Database Design

## Overview
BloodLink uses a relational database (PostgreSQL) with 11 core tables supporting user management, blood inventory, request coordination, donor matching, and audit logging.

## Entity Relationship Diagram

```
┌──────────────┐     1:1      ┌──────────────────┐
│    users     │─────────────▶│  donor_profiles  │
│              │              │                  │
│  id (PK)     │              │  id (PK)         │
│  full_name   │              │  user_id (FK)    │
│  email       │    1:*       │  blood_group     │
│  phone       │───────┐     │  city            │
│  password_hash│      │     │  availability    │
│  role        │      │     │  verification    │
│  is_active   │      │     └──────────────────┘
│  created_at  │      │              │
│  updated_at  │      │              │ 1:*
└──────────────┘      │              ▼
       │              │     ┌──────────────────┐
       │ 1:*          │     │  donor_matches   │
       │              │     │                  │
       ▼              │     │  id (PK)         │
┌──────────────┐      │     │  request_id (FK) │
│  blood_      │      │     │  donor_id (FK)   │
│  requests    │◀─────┘     │  match_score     │
│              │            │  status          │
│  id (PK)     │──────────▶│                  │
│  requester_id│   1:*      └──────────────────┘
│  hospital_id │
│  blood_group │     ┌──────────────────┐
│  component   │     │   donations      │
│  units_req   │     │                  │
│  priority    │     │  id (PK)         │
│  status      │     │  donor_id (FK)   │
└──────────────┘     │  donation_date   │
       ▲             │  blood_group     │
       │             │  status          │
       │             └──────────────────┘
  ┌────┘
  │
┌──────────────┐     1:*     ┌──────────────────┐
│  hospitals   │────────────▶│  blood_inventory │
│              │             │                  │
│  id (PK)     │             │  id (PK)         │
│  user_id(FK) │             │  hospital_id(FK) │
│  name        │             │  blood_group     │
│  type        │             │  component       │
│  city        │             │  available_units │
│  state       │             │  reserved_units  │
│  verification│             │  source_type     │
└──────────────┘             └──────────────────┘

┌──────────────┐  ┌──────────────────┐  ┌────────────────┐
│ notifications│  │ external_blood_  │  │  audit_logs    │
│              │  │ records          │  │                │
│  id (PK)     │  │  id (PK)         │  │  id (PK)       │
│  user_id(FK) │  │  provider_name   │  │  user_id (FK)  │
│  type        │  │  blood_group     │  │  action        │
│  title       │  │  units_available │  │  entity_type   │
│  message     │  │  city/state      │  │  description   │
│  is_read     │  │  fetched_at      │  │  ip_address    │
└──────────────┘  └──────────────────┘  └────────────────┘

┌──────────────┐
│  api_sources │
│              │
│  id (PK)     │
│  name        │
│  source_type │
│  enabled     │
│  last_sync   │
└──────────────┘
```

## Table Details

### users
Primary user table for all roles.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | Auto-increment ID |
| full_name | VARCHAR(150) | NOT NULL | User's display name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| phone | VARCHAR(20) | | Contact number |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt/PBKDF2 hash |
| role | VARCHAR(20) | NOT NULL | PATIENT, DONOR, HOSPITAL, ADMIN |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW | |
| updated_at | TIMESTAMP | ON UPDATE | |

### donor_profiles
Extended profile for donors.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | |
| user_id | INTEGER | FK → users, UNIQUE | One profile per user |
| blood_group | VARCHAR(5) | NOT NULL | A+, A-, B+, B-, AB+, AB-, O+, O- |
| city | VARCHAR(100) | | Approximate city |
| area | VARCHAR(100) | | Approximate area |
| latitude | FLOAT | | Approximate (rounded for privacy) |
| longitude | FLOAT | | Approximate (rounded for privacy) |
| availability_status | VARCHAR(20) | DEFAULT 'AVAILABLE' | AVAILABLE, UNAVAILABLE |
| verification_status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING, VERIFIED, REJECTED |
| last_donation_date | TIMESTAMP | NULLABLE | |

### hospitals
Hospital and blood bank organizations.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | |
| user_id | INTEGER | FK → users, NULLABLE | Linked user account |
| name | VARCHAR(255) | NOT NULL | Organization name |
| type | VARCHAR(50) | | BLOOD_BANK, HOSPITAL, CLINIC |
| address | TEXT | | Full address |
| city | VARCHAR(100) | | City |
| state | VARCHAR(100) | | State |
| verification_status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING, VERIFIED, REJECTED |

### blood_inventory
Current blood stock at each hospital.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | |
| hospital_id | INTEGER | FK → hospitals, NOT NULL | Owning hospital |
| blood_group | VARCHAR(5) | NOT NULL | Blood type |
| component | VARCHAR(50) | NOT NULL | WHOLE_BLOOD, PACKED_RED_CELLS, PLASMA, PLATELETS |
| available_units | INTEGER | DEFAULT 0, ≥ 0 | Units available |
| reserved_units | INTEGER | DEFAULT 0, ≥ 0 | Units reserved |
| source_type | VARCHAR(20) | DEFAULT 'LOCAL' | LOCAL, EXTERNAL, DEMO |
| **UNIQUE** | | (hospital_id, blood_group, component) | |

### blood_requests
Blood requests from patients/users.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | |
| requester_id | INTEGER | FK → users | Who requested |
| hospital_id | INTEGER | FK → hospitals, NULLABLE | Destination hospital |
| blood_group | VARCHAR(5) | NOT NULL | Required blood type |
| component | VARCHAR(50) | DEFAULT 'WHOLE_BLOOD' | |
| units_required | INTEGER | NOT NULL, > 0 | |
| priority | VARCHAR(20) | DEFAULT 'NORMAL' | NORMAL, URGENT, EMERGENCY |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING → MATCHING → FULFILLED/CANCELLED |

### donor_matches
Matches between requests and potential donors.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PK | |
| request_id | INTEGER | FK → blood_requests | |
| donor_id | INTEGER | FK → donor_profiles | |
| match_score | FLOAT | | 0-100 compatibility score |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING, NOTIFIED, ACCEPTED, DECLINED, EXPIRED |

## Indexes
- `users.email` — Login lookups
- `donor_profiles.blood_group` — Donor matching queries
- `donor_profiles.city` — Location-based searches
- `blood_inventory.blood_group` — Availability searches
- `blood_inventory.hospital_id` — Hospital inventory views
- `blood_requests.blood_group` — Request matching
- `blood_requests.status` — Status-filtered lists
- `blood_requests.created_at` — Chronological sorting
- `audit_logs.created_at` — Audit log browsing

## Data Integrity Rules
1. Blood inventory units cannot be negative
2. Unique constraint on (hospital_id, blood_group, component) prevents duplicate entries
3. Every inventory modification creates an audit log entry
4. Password hashes are never exposed in API responses
5. Donor exact coordinates are rounded for privacy in API responses
6. External data records are clearly tagged with source and fetch timestamp
