# BloodLink — API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Response Format

### Success
```json
{
  "success": true,
  "data": { ... }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Paginated
```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

---

## Authentication

### Register
```
POST /api/v1/auth/register
```
**Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "phone": "+91-9876543210",
  "role": "PATIENT",
  "donor_data": {
    "blood_group": "B+",
    "city": "Kolkata",
    "area": "Salt Lake"
  },
  "hospital_data": {
    "name": "City Hospital",
    "type": "HOSPITAL",
    "address": "123 Medical Road",
    "city": "Kolkata",
    "state": "West Bengal"
  }
}
```
- `donor_data` required when role = "DONOR"
- `hospital_data` required when role = "HOSPITAL"

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "full_name": "John Doe", "email": "john@example.com", "role": "PATIENT" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### Login
```
POST /api/v1/auth/login
```
**Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": { ... },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### Refresh Token
```
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```
**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ..."
  }
}
```

### Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

---

## Blood Availability

### Search Blood Availability
```
GET /api/v1/blood/availability
```
**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| blood_group | string | No | A+, A-, B+, B-, AB+, AB-, O+, O- |
| component | string | No | WHOLE_BLOOD, PACKED_RED_CELLS, PLASMA, PLATELETS |
| city | string | No | City name |
| state | string | No | State name |
| source | string | No | Filter by source: local, external, demo |

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "blood_bank": "City Demo Hospital",
        "location": { "city": "Kolkata", "state": "West Bengal" },
        "blood_group": "B+",
        "component": "WHOLE_BLOOD",
        "available_units": 8,
        "source": "Demo Data",
        "last_updated": "2026-10-05T10:30:00Z",
        "data_freshness": "Updated 15 minutes ago"
      }
    ],
    "meta": {
      "total_results": 1,
      "sources_queried": ["BloodLink Database", "Demo Data"],
      "external_provider_status": "available"
    }
  }
}
```

### Get Blood Groups
```
GET /api/v1/blood/groups
```

---

## Blood Requests

### Create Blood Request
```
POST /api/v1/requests
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "blood_group": "B+",
  "component": "WHOLE_BLOOD",
  "units_required": 3,
  "hospital_id": 1,
  "required_by": "2026-10-06T10:00:00Z",
  "priority": "URGENT",
  "notes": "Needed for scheduled surgery"
}
```
**Roles:** PATIENT, DONOR

### List Requests
```
GET /api/v1/requests?page=1&per_page=20&status=PENDING&blood_group=B%2B
Authorization: Bearer <access_token>
```
- PATIENT sees own requests
- HOSPITAL sees requests for their hospital
- ADMIN sees all requests

### Get Request Details
```
GET /api/v1/requests/<id>
Authorization: Bearer <access_token>
```

### Update Request
```
PATCH /api/v1/requests/<id>
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "status": "FULFILLED",
  "notes": "Fulfilled by Metro Blood Bank"
}
```
**Roles:** Request owner, HOSPITAL, ADMIN

### Cancel Request
```
POST /api/v1/requests/<id>/cancel
Authorization: Bearer <access_token>
```
**Roles:** Request owner, ADMIN

---

## Donors

### List Donors
```
GET /api/v1/donors?blood_group=B%2B&city=Kolkata&availability=AVAILABLE
Authorization: Bearer <access_token>
```
**Roles:** HOSPITAL, ADMIN

### Get Donor Details
```
GET /api/v1/donors/<id>
Authorization: Bearer <access_token>
```
> Note: Exact location is never exposed. Only approximate area is shown.

### Get Matching Donors for Request
```
GET /api/v1/donors/matches/<request_id>
Authorization: Bearer <access_token>
```
**Roles:** Request owner, HOSPITAL, ADMIN

**Response:**
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "donor_id": 1,
        "blood_group": "B+",
        "approximate_location": "Salt Lake, Kolkata",
        "match_score": 90,
        "availability": "AVAILABLE",
        "status": "PENDING",
        "reasons": ["Exact blood group match", "Same city", "Verified donor"]
      }
    ]
  }
}
```

### Update Donor Profile
```
PATCH /api/v1/donors/profile
Authorization: Bearer <access_token>
```
**Roles:** DONOR

### Update Donor Availability
```
PATCH /api/v1/donors/availability
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "availability_status": "AVAILABLE"
}
```
**Roles:** DONOR

---

## Hospitals

### List Hospitals
```
GET /api/v1/hospitals?city=Kolkata&state=West+Bengal
```

### Get Hospital Details
```
GET /api/v1/hospitals/<id>
```

### Get Hospital Inventory
```
GET /api/v1/hospitals/<id>/inventory
```

---

## Inventory

### Add Inventory
```
POST /api/v1/inventory
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "hospital_id": 1,
  "blood_group": "B+",
  "component": "WHOLE_BLOOD",
  "available_units": 10,
  "source_type": "LOCAL"
}
```
**Roles:** HOSPITAL

### Update Inventory
```
PATCH /api/v1/inventory/<id>
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "available_units": 7,
  "reserved_units": 2
}
```
**Roles:** HOSPITAL (own inventory), ADMIN

### List Inventory
```
GET /api/v1/inventory?blood_group=B%2B&component=WHOLE_BLOOD
Authorization: Bearer <access_token>
```
**Roles:** HOSPITAL (own), ADMIN (all)

---

## Donations

### Record Donation
```
POST /api/v1/donations
Authorization: Bearer <access_token>
```
**Roles:** DONOR, HOSPITAL

### List Donations
```
GET /api/v1/donations
Authorization: Bearer <access_token>
```
**Roles:** DONOR (own), HOSPITAL (at their location), ADMIN (all)

---

## Notifications

### Get Notifications
```
GET /api/v1/notifications?unread_only=true&page=1
Authorization: Bearer <access_token>
```

### Mark Notification as Read
```
PATCH /api/v1/notifications/<id>/read
Authorization: Bearer <access_token>
```

---

## Admin

### Get Statistics
```
GET /api/v1/admin/statistics
Authorization: Bearer <access_token>
```
**Roles:** ADMIN

### List Users
```
GET /api/v1/admin/users?role=DONOR&is_active=true&search=john
Authorization: Bearer <access_token>
```
**Roles:** ADMIN

### Get Audit Logs
```
GET /api/v1/admin/audit-logs?action=INVENTORY_UPDATE&date_from=2026-10-01
Authorization: Bearer <access_token>
```
**Roles:** ADMIN

### Verify Hospital
```
PATCH /api/v1/admin/hospitals/<id>/verify
Authorization: Bearer <access_token>
```
**Body:**
```json
{
  "verification_status": "VERIFIED"
}
```
**Roles:** ADMIN

---

## WebSocket Events (Socket.IO)

### Connection
```javascript
const socket = io('http://localhost:5000', {
  auth: { token: 'Bearer <access_token>' }
});
```

### Events
| Event | Direction | Description |
|-------|-----------|-------------|
| `inventory_updated` | Server → Client | Blood inventory was modified |
| `new_blood_request` | Server → Client | New blood request created |
| `donor_match_found` | Server → Client | Matching donor found for request |
| `request_status_changed` | Server → Client | Request status was updated |
| `notification_created` | Server → Client | New notification for user |

---

## Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |
