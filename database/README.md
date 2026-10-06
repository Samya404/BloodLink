# BloodLink Database

## Overview
BloodLink uses **PostgreSQL** as its primary database, with **SQLite** as an optional fallback for simple local development.

## Schema Management
The database schema is managed by **Flask-Migrate** (Alembic) for version-controlled migrations.

### Files in this directory
| File | Purpose |
|------|---------|
| `schema.sql` | Reference SQL schema (for documentation; actual schema is managed by Flask-Migrate) |
| `seed.sql` | Demo/seed data SQL (for reference; use `flask seed` CLI command for working seed data) |

## Setup

### Option 1: Flask-Migrate (Recommended)
```bash
cd backend
flask db init        # Initialize migrations (first time only)
flask db migrate     # Generate migration from models
flask db upgrade     # Apply migration to database
flask seed           # Seed demo data with proper password hashes
```

### Option 2: Direct SQL (Reference)
```bash
psql -U postgres -d bloodlink -f database/schema.sql
psql -U postgres -d bloodlink -f database/seed.sql
```
> **Note**: The SQL seed file uses placeholder password hashes. Use `flask seed` for working demo accounts.

### Option 3: Docker
```bash
docker-compose up -d db
# Schema is auto-applied from docker-entrypoint-initdb.d
```

## Database Configuration

### PostgreSQL (Default/Production)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/bloodlink
```

### SQLite (Development Fallback)
```
DATABASE_URL=sqlite:///bloodlink.db
```

## Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@bloodlink.demo | Password123! |
| Donor | donor@bloodlink.demo | Password123! |
| Patient | patient@bloodlink.demo | Password123! |
| Hospital | hospital@bloodlink.demo | Password123! |

> ⚠️ **These are demo accounts only.** Change passwords in any non-development environment.

## Entity Relationship Diagram

```
users 1──1 donor_profiles
users 1──* blood_requests
users 1──* notifications
users 1──* audit_logs
hospitals 1──* blood_inventory
hospitals 1──* blood_requests
blood_requests 1──* donor_matches
donor_profiles 1──* donor_matches
donor_profiles 1──* donations
```

## Tables
1. **users** — All user accounts (patients, donors, hospitals, admins)
2. **donor_profiles** — Donor-specific information and availability
3. **hospitals** — Hospital/blood bank organization records
4. **blood_inventory** — Current blood stock at each hospital
5. **blood_requests** — Blood requests from patients
6. **donor_matches** — Matched donors for each request
7. **donations** — Donation history
8. **notifications** — User notifications
9. **api_sources** — External API configuration
10. **external_blood_records** — Cached data from external providers
11. **audit_logs** — System audit trail
