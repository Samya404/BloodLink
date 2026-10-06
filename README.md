# 🩸 BloodLink — Real-Time Blood Availability & Donor Network

<div align="center">

**Find Blood When It Matters Most.**

A full-stack blood availability and donor coordination platform that enables real-time blood searching, request management, donor matching, and hospital inventory tracking.

[Features](#features) · [Tech Stack](#technology-stack) · [Setup](#quick-start) · [API Docs](docs/api-documentation.md) · [Architecture](docs/architecture.md)

</div>

---

## Features

### 🔍 Blood Availability Search
- Search by blood group, component, city, and state
- Real-time availability from hospitals and blood banks
- External data provider integration (with authorized API access)
- Data freshness indicators and source labels

### 🏥 Hospital / Blood Bank Dashboard
- Manage blood inventory (add, update, remove stock)
- Low stock alerts and notifications
- Track blood requests and fulfillment
- Audit trail for all inventory changes

### 🩸 Donor Network
- Donor registration with blood group and location
- Availability management (Available/Unavailable toggle)
- Automatic matching with compatible blood requests
- Privacy-protected — exact location never shared

### 📋 Blood Request System
- Create requests with priority levels (Normal, Urgent, Emergency)
- Real-time status tracking (Pending → Matching → Fulfilled)
- Automatic donor matching based on blood group compatibility
- Notification system for matched donors

### 🔔 Real-Time Notifications
- Socket.IO powered live updates
- Inventory change notifications
- Blood request match alerts
- Low stock warnings

### 🛡️ Admin Dashboard
- User management and verification
- System-wide statistics and charts
- Hospital verification workflow
- Comprehensive audit logging

### 🔐 Security
- JWT authentication (access + refresh tokens)
- Role-based access control (Patient, Donor, Hospital, Admin)
- Password hashing (PBKDF2)
- Input validation and SQL injection prevention
- Audit logging for all write operations

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Fetch API, Socket.IO Client |
| **Backend** | Python 3.12+, Flask, Flask-SocketIO |
| **Database** | PostgreSQL (primary), SQLite (dev fallback) |
| **ORM** | SQLAlchemy, Flask-Migrate |
| **Auth** | Flask-JWT-Extended |
| **Validation** | Marshmallow |
| **Real-time** | Flask-SocketIO (WebSockets) |

---

## Architecture

```
Browser (HTML/CSS/JS) ──── REST API + WebSocket ──── Flask Backend
                                                        │
                                              ┌─────────┼─────────┐
                                              │         │         │
                                          SQLAlchemy  Socket.IO  External
                                              │                  Provider
                                          PostgreSQL         ┌─────────┐
                                                             │ Mock    │
                                                             │ eRaktK. │
                                                             └─────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

---

## Project Structure

```
BloodLink/
├── frontend/                   # Client-side application
│   ├── index.html              # Landing page
│   ├── login.html              # Login
│   ├── register.html           # Registration
│   ├── blood-search.html       # Blood availability search
│   ├── patient-dashboard.html  # Patient dashboard
│   ├── donor-dashboard.html    # Donor dashboard
│   ├── hospital-dashboard.html # Hospital dashboard
│   ├── admin-dashboard.html    # Admin dashboard
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript modules
│
├── backend/                    # Flask server
│   ├── app.py                  # Application factory
│   ├── config.py               # Configuration
│   ├── extensions.py           # Flask extensions
│   ├── models/                 # SQLAlchemy models
│   ├── routes/                 # API route blueprints
│   ├── services/               # Business logic
│   ├── schemas/                # Marshmallow schemas
│   ├── utils/                  # Helpers & decorators
│   └── tests/                  # Automated tests
│
├── database/                   # DB reference files
│   ├── schema.sql              # Reference schema
│   ├── seed.sql                # Demo data
│   └── README.md               # Database docs
│
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── api-documentation.md
│   ├── database-design.md
│   └── setup.md
│
├── .env.example                # Environment template
├── .gitignore
├── docker-compose.yml          # Docker setup
└── README.md                   # This file
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 14+ (or use SQLite for quick start)

### 1. Clone & Configure
```bash
git clone <repository-url>
cd BloodLink
cp .env.example .env
# Edit .env — set SECRET_KEY and JWT_SECRET_KEY to random strings
```

### 2. Set Up Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### 3. Initialize Database

**With PostgreSQL:**
```bash
psql -U postgres -c "CREATE DATABASE bloodlink;"
# Ensure DATABASE_URL in .env points to your PostgreSQL
```

**With SQLite (quick start):**
```bash
# In .env, set: DATABASE_URL=sqlite:///bloodlink.db
```

```bash
set FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed
```

### 4. Run
```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### Docker Alternative
```bash
docker-compose up -d
```

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@bloodlink.demo | Password123! |
| Patient | patient@bloodlink.demo | Password123! |
| Donor | donor@bloodlink.demo | Password123! |
| Hospital | hospital@bloodlink.demo | Password123! |

> ⚠️ Demo accounts are for development only. Change passwords in production.

---

## API Overview

Base URL: `http://localhost:5000/api/v1`

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login |
| `/auth/me` | GET | Current user info |
| `/blood/availability` | GET | Search blood availability |
| `/blood/groups` | GET | List blood groups |
| `/requests` | GET, POST | Blood requests |
| `/requests/<id>` | GET, PATCH | Request details |
| `/donors` | GET | List donors |
| `/donors/profile` | PATCH | Update donor profile |
| `/donors/availability` | PATCH | Update availability |
| `/donors/matches/<id>` | GET | Get matching donors |
| `/hospitals` | GET | List hospitals |
| `/hospitals/<id>/inventory` | GET | Hospital inventory |
| `/inventory` | GET, POST | Manage inventory |
| `/inventory/<id>` | PATCH | Update inventory |
| `/notifications` | GET | User notifications |
| `/admin/statistics` | GET | Admin statistics |
| `/admin/users` | GET | Admin user management |
| `/admin/audit-logs` | GET | Audit log viewer |

See [docs/api-documentation.md](docs/api-documentation.md) for full API reference.

---

## External API Integration

BloodLink is designed to integrate with external blood availability providers.

### Mock Provider (Default)
Used for development. Returns realistic demo data for cities like Kolkata, Delhi, Mumbai, and Bengaluru. All data clearly labeled as **"Demo Data"**.

### e-RaktKosh Provider
Designed for integration with India's e-RaktKosh blood availability ecosystem, **subject to authorized API access**.

> **Important:** The e-RaktKosh provider requires valid API credentials. The application does NOT scrape websites, bypass authentication, or reverse-engineer protected endpoints. If credentials are not configured, the mock provider is used automatically.

To enable:
```env
BLOOD_PROVIDER=eraktkosh
ERAKTKOSH_API_BASE_URL=<authorized-api-url>
ERAKTKOSH_API_KEY=<your-api-key>
```

---

## Running Tests
```bash
cd backend
python -m pytest tests/ -v
```

---

## Security Notes

- Passwords are hashed using PBKDF2 (Werkzeug)
- JWT tokens for stateless authentication
- Role-based access control on all protected endpoints
- SQL injection prevented via SQLAlchemy parameterized queries
- Sensitive data (passwords, tokens, API keys) never logged
- CORS configured via environment variables
- Audit logging for all data modifications
- Donor exact locations never exposed — only approximate area shown

---

## Limitations

- **Not a medical decision system**: BloodLink is a coordination platform. Blood group compatibility matching is for informational/coordination purposes only and does not replace professional medical/blood-bank compatibility verification.
- **Demo data**: When using the mock provider, all external blood data is fictional demo data.
- **External API**: e-RaktKosh integration requires authorized API access that must be separately arranged.
- **Push notifications**: Firebase Cloud Messaging integration is optional and requires separate configuration.
- **Maps**: Map features require a Google Maps API key or OpenStreetMap service configuration.

---

## Future Improvements

- [ ] Mobile application (React Native / Flutter)
- [ ] SMS notifications via Twilio
- [ ] Blood drive event management
- [ ] Analytics and reporting dashboard
- [ ] Multi-language support (Hindi, Bengali, etc.)
- [ ] Donor eligibility questionnaire
- [ ] Integration with more blood bank networks
- [ ] Progressive Web App (PWA) support
- [ ] Email verification and password reset
- [ ] Two-factor authentication

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a Pull Request

---

## License

This project is developed as a college software engineering project.

---

<div align="center">
Built with ❤️ for saving lives.
</div>
