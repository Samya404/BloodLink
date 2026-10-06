# BloodLink — Architecture

## System Overview

BloodLink is a **Real-Time Blood Availability & Donor Network** platform built with a modular, layered architecture designed for maintainability, security, and extensibility.

## High-Level Architecture

```
┌─────────────────────────────┐
│       USER BROWSER          │
│                             │
│  HTML5 + CSS3 + Vanilla JS  │
│  Fetch API + Socket.IO      │
└──────────────┬──────────────┘
               │
          HTTPS / REST API
          WebSocket (Socket.IO)
               │
┌──────────────▼──────────────┐
│       FLASK BACKEND         │
│                             │
│  ┌─────────────────────┐    │
│  │   Route Layer       │    │
│  │   (Blueprints)      │    │
│  └────────┬────────────┘    │
│  ┌────────▼────────────┐    │
│  │   Service Layer     │    │
│  │   (Business Logic)  │    │
│  └────────┬────────────┘    │
│  ┌────────▼────────────┐    │
│  │   Data Layer        │    │
│  │   (SQLAlchemy ORM)  │    │
│  └────────┬────────────┘    │
│  ┌────────▼────────────┐    │
│  │   Schema Layer      │    │
│  │   (Marshmallow)     │    │
│  └─────────────────────┘    │
└───────┬──────────┬──────────┘
        │          │
   SQLAlchemy    Socket.IO
        │          │
        ▼          ▼
┌──────────────┐  Real-time
│  PostgreSQL  │  events to
│  (or SQLite) │  connected
└──────────────┘  clients
        ▲
        │
┌───────┴──────────────┐
│  External Providers  │
│                      │
│  ┌────────────────┐  │
│  │ e-RaktKosh     │  │
│  │ (when avail.)  │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ MockProvider   │  │
│  │ (demo data)    │  │
│  └────────────────┘  │
└──────────────────────┘
```

## Layer Descriptions

### Frontend Layer
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **No frameworks**: No React, Angular, or Vue
- **Communication**: REST API via Fetch, real-time via Socket.IO client
- **State**: JWT tokens stored in localStorage
- **Routing**: File-based (each page is a separate HTML file)

### Route Layer (API Endpoints)
- Flask Blueprints organized by domain
- API versioned under `/api/v1`
- JWT authentication via `@jwt_required()`
- Role-based access via custom decorators
- Input validation via Marshmallow schemas
- Consistent JSON response format

### Service Layer (Business Logic)
- **AuthService**: Registration, login, token management
- **MatchingService**: Blood group compatibility, donor matching
- **InventoryService**: Stock management, low-stock alerts
- **NotificationService**: Real-time notifications via Socket.IO
- **ExternalBloodProvider**: Adapter pattern for external data sources

### Data Layer (ORM)
- SQLAlchemy models with relationships
- Flask-Migrate for schema versioning
- PostgreSQL (production) / SQLite (development fallback)
- Proper indexes for query performance

### Schema Layer (Validation)
- Marshmallow schemas for request/response validation
- Separate schemas for input validation and output serialization
- Centralized validation rules

## Security Architecture

```
Request → CORS Check → JWT Validation → Role Check → Input Validation → Handler
                                                                           │
                                                                     Audit Log
```

- **Authentication**: JWT tokens (access + refresh)
- **Authorization**: Role-based (PATIENT, DONOR, HOSPITAL, ADMIN)
- **Password Storage**: Werkzeug PBKDF2 hashing
- **Input Validation**: Marshmallow schemas + custom validators
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **CORS**: Configurable allowed origins
- **Audit Trail**: All write operations logged

## External API Architecture

The external blood provider system uses the **Adapter Pattern**:

```
ExternalBloodProvider (Abstract Base Class)
    ├── ERaktKoshProvider  (requires API credentials)
    └── MockBloodProvider  (demo data, always available)
```

- Provider selection via `BLOOD_PROVIDER` environment variable
- Graceful fallback when external provider is unavailable
- Data source clearly labeled (BloodLink Database / External Provider / Demo Data)
- Stale data warnings when timestamps indicate outdated information

## Real-Time Architecture

```
Client A ──── Socket.IO ────┐
Client B ──── Socket.IO ────┤
Client C ──── Socket.IO ────┼──── Flask-SocketIO Server
                            │         │
                            │    Event Types:
                            │    • inventory_updated
                            │    • new_blood_request
                            │    • donor_match_found
                            │    • request_status_changed
                            │    • notification_created
                            │
                            └──── REST API (source of truth)
```

- WebSocket events for live UI updates
- REST API remains the authoritative data source
- Socket.IO rooms for targeted notifications (per-user, per-hospital)

## Data Flow: Blood Availability Search

```
1. User searches: "B+ in Kolkata"
2. Frontend: GET /api/v1/blood/availability?blood_group=B%2B&city=Kolkata
3. Backend:
   a. Validate request parameters
   b. Query local blood_inventory table
   c. Query external_blood_records (cached external data)
   d. If external provider enabled: query provider API
   e. Normalize and combine results
   f. Add data freshness information
4. Response includes source labels and timestamps
5. Frontend displays results with freshness indicators
```
