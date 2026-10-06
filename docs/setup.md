# BloodLink — Setup Guide

## Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/)) — or use SQLite for quick local dev
- **Git** ([Download](https://git-scm.com/))
- **Docker** (optional, [Download](https://www.docker.com/))

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd BloodLink
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (at minimum, set SECRET_KEY and JWT_SECRET_KEY)
```

### 3. Set Up the Backend

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Set Up Database

**Option A: PostgreSQL (Recommended)**
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE bloodlink;"

# Set in .env:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/bloodlink
```

**Option B: SQLite (Quick Dev)**
```bash
# Set in .env:
# DATABASE_URL=sqlite:///bloodlink.db
```

#### Initialize Database & Seed Data
```bash
# Set Flask app
set FLASK_APP=app.py      # Windows
export FLASK_APP=app.py    # macOS/Linux

# Initialize migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed demo data
flask seed
```

### 4. Start the Backend
```bash
python app.py
```
The backend will start at `http://localhost:5000`

### 5. Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```
The Flask backend serves the frontend files directly.

---

## Docker Setup (Alternative)

### Start Everything
```bash
docker-compose up -d
```

### Stop
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@bloodlink.demo | Password123! |
| **Donor** | donor@bloodlink.demo | Password123! |
| **Patient** | patient@bloodlink.demo | Password123! |
| **Hospital** | hospital@bloodlink.demo | Password123! |

> ⚠️ These are for development/demo only. Change in any non-dev environment.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | development | Flask environment |
| `SECRET_KEY` | **Yes** | change-me | Flask secret key |
| `JWT_SECRET_KEY` | **Yes** | change-me | JWT signing key |
| `DATABASE_URL` | **Yes** | postgresql://... | Database connection |
| `BLOOD_PROVIDER` | No | mock | Blood data provider |
| `ERAKTKOSH_API_BASE_URL` | No | | e-RaktKosh API URL |
| `ERAKTKOSH_API_KEY` | No | | e-RaktKosh API key |
| `GOOGLE_MAPS_API_KEY` | No | | Google Maps key |
| `HOST` | No | 0.0.0.0 | Server host |
| `PORT` | No | 5000 | Server port |

---

## Running Tests
```bash
cd backend
python -m pytest tests/ -v
```

---

## Troubleshooting

### "ModuleNotFoundError"
Make sure the virtual environment is activated:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### PostgreSQL Connection Error
1. Verify PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Verify the `bloodlink` database exists
4. Try SQLite fallback: set `DATABASE_URL=sqlite:///bloodlink.db`

### "Address already in use"
Another process is using port 5000. Either:
- Stop the other process
- Change `PORT` in `.env`

### Database Migration Issues
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Fresh start"
flask db upgrade
flask seed
```

### CORS Errors
Check `CORS_ORIGINS` in `.env` matches your frontend URL.

### Socket.IO Connection Issues
- Ensure eventlet is installed: `pip install eventlet`
- Check browser console for WebSocket errors
- Verify JWT token is valid
