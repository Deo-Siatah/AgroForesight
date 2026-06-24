# Hifadhi API Routes

Base URL: `http://127.0.0.1:8000`

## Authentication

JWT-based. All protected routes require a bearer token obtained from `POST /api/v1/auth/login`.
Tokens are signed with HS256. Default TTL is 24 hours (configurable via `AUTH_TOKEN_TTL_MINUTES`).

Include the token on every protected request:
```
Authorization: Bearer <access_token>
```

### Endpoints

- `POST /api/v1/auth/login` — exchange email + password for a bearer token.
- `GET /api/v1/auth/me` — return the currently authenticated user. Requires any valid token.

### Seeded users

| Email | Password | Role |
|---|---|---|
| `admin26@gmail.com` | `admin26` | `admin` |
| `saccoadmin26@gmail.com` | `saccoadmin26` | `sacco_admin` |

---

## Roles

| Role | Scope |
|---|---|
| `admin` | Full access to all resources across all SACCOs. |
| `sacco_admin` | Read/write access scoped to their own SACCO only. |
| `farmer` | Read-only access to their own farmer profile (`GET /farmers/{id}`). |
| `extension_officer` | Defined but not yet granted access to any endpoint. |

Role enforcement is applied at both the route layer (authentication + role check) and the service layer (ownership scoping). A `sacco_admin` cannot access or modify resources that belong to a different SACCO even if they have a valid token.

---

## Error responses

| Status | Meaning |
|---|---|
| `401` | Missing or invalid bearer token. |
| `403` | Authenticated but insufficient role or wrong SACCO scope. |
| `404` | Resource not found. |
| `409` | Conflict — duplicate phone, national ID, or email. |
| `422` | Validation error — invalid input shape or business rule violation (e.g. invalid status transition, bad coordinates). |

---

## Health

- `GET /health` — server health check. No auth required.

---

## Saccos

All SACCO endpoints require `admin` role.

- `POST /api/v1/saccos` — create a SACCO and provision its `sacco_admin` user.
- `GET /api/v1/saccos` — list SACCOs. Supports `?offset=0&limit=20` pagination.
- `GET /api/v1/saccos/{sacco_id}` — fetch one SACCO.

### POST /api/v1/saccos — request body

```json
{
  "name": "Kilimo SACCO",
  "county": "Nakuru",
  "admin_email": "admin@kilimo.co.ke",
  "admin_password": "securepassword"
}
```

`county` is optional. `name`, `admin_email`, and `admin_password` must not be blank.

---

## Farmers

- `POST /api/v1/farmers` — register a farmer and provision their login account. Requires `admin` or `sacco_admin` (own SACCO only).
- `GET /api/v1/farmers/{farmer_id}` — fetch a farmer profile (farmer + farms + loans). Requires `admin`, the owning `sacco_admin`, or the farmer themselves.

### POST /api/v1/farmers — request body

```json
{
  "sacco_id": "<uuid>",
  "first_name": "Jane",
  "last_name": "Wanjiku",
  "phone": "+254712345678",
  "national_id": "12345678",
  "login_email": "jane@hifadhi.local",
  "login_password": "securepassword"
}
```

- `national_id` is optional.
- `phone` must contain only digits with an optional leading `+`. All-zero values are rejected.
- `national_id` must contain only digits if provided. All-zero values are rejected.
- Duplicate `phone`, `national_id`, or `login_email` returns `409`.

---

## Farms

All farm endpoints require `admin` or `sacco_admin` (own SACCO only). The `farmer` role is blocked.

- `POST /api/v1/farms` — create a farm for a farmer.
- `GET /api/v1/farms/{farm_id}` — fetch one farm. A `farmer` user can only fetch their own farms.

### POST /api/v1/farms — request body

```json
{
  "farmer_id": "<uuid>",
  "name": "Wanjiku Maize Farm",
  "county": "Nakuru",
  "acreage": "2.50",
  "latitude": -0.30,
  "longitude": 36.10
}
```

- `acreage` must be greater than 0.
- `latitude` must be within Kenya's bounding box: `-5.0` to `5.0`.
- `longitude` must be within Kenya's bounding box: `33.5` to `42.0`.
- `name` and `county` must not be blank.

---

## Seasons

All season endpoints require `admin` or `sacco_admin` (own SACCO only). The `farmer` role is blocked.

- `POST /api/v1/seasons` — create a season for a farm. Always starts as `planned`.
- `GET /api/v1/seasons/{season_id}` — fetch one season.
- `PATCH /api/v1/seasons/{season_id}/activate` — transition `planned → active`.
- `PATCH /api/v1/seasons/{season_id}/harvest` — transition `active → harvested`.
- `PATCH /api/v1/seasons/{season_id}/fail` — transition `active → failed`.

### POST /api/v1/seasons — request body

```json
{
  "farm_id": "<uuid>",
  "crop_type": "Maize",
  "planting_date": "2025-03-01",
  "expected_harvest_date": "2025-07-01"
}
```

- `expected_harvest_date` must be after `planting_date`.
- `crop_type` must not be blank.

### Status transitions

```
planned → active → harvested (terminal)
                 → failed    (terminal)
```

Any other transition returns `422`. Terminal states cannot be exited.

---

## Loans

All loan endpoints require `admin` or `sacco_admin` (own SACCO only). The `farmer` role is blocked.

- `POST /api/v1/loans` — create a loan for a farmer. Always starts as `pending`.
- `GET /api/v1/loans/{loan_id}` — fetch one loan.
- `PATCH /api/v1/loans/{loan_id}/approve` — transition `pending → approved`.
- `PATCH /api/v1/loans/{loan_id}/reject` — transition `pending | approved → rejected`.
- `PATCH /api/v1/loans/{loan_id}/disburse` — transition `approved → disbursed`.
- `PATCH /api/v1/loans/{loan_id}/activate` — transition `disbursed → active`.
- `PATCH /api/v1/loans/{loan_id}/repay` — transition `active → repaid`.
- `PATCH /api/v1/loans/{loan_id}/default` — transition `active → defaulted`.
- `GET /api/v1/loans/{loan_id}/risk` — compute risk score. Accepts optional `?season_id=<uuid>`.
- `POST /api/v1/loans/{loan_id}/risk/recalculate` — force a fresh risk calculation. Accepts optional `?season_id=<uuid>`.

### POST /api/v1/loans — request body

```json
{
  "farmer_id": "<uuid>",
  "amount": "120000.00",
  "season_id": "<uuid>"
}
```

- `amount` must be greater than 0.
- `season_id` is optional but recommended — risk scoring is weaker without it.

### Status transitions

```
pending → approved  → disbursed → active → repaid    (terminal)
        → rejected               (terminal)        → defaulted (terminal)
        ↑
  approved → rejected (terminal)
```

Any other transition returns `422`. Terminal states (`repaid`, `defaulted`, `rejected`) cannot be exited.

### Risk score

| Condition | Points |
|---|---|
| Season status is `failed` | +40 |
| Weather alert (Phase 2) | +15 |
| Missed recommendation (Phase 2) | +20 |

| Score | Category |
|---|---|
| 0 – 30 | `low` |
| 31 – 60 | `medium` |
| 61 – 100 | `high` |

Score is capped at 100.
