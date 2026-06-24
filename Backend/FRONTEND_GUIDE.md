# Hifadhi — Frontend Integration Guide (Lovable)

> **Purpose:** This file is the single source of truth for building the Hifadhi frontend.
> It documents every API route, the exact JSON shapes required and returned, the role-permission
> model, status-machine constraints, and guidance on what UI component maps to what route.
>
> **Base URL (dev):** `http://127.0.0.1:8000`
> **API prefix:** Every route lives under `/api/v1/` except the health check.

---

## 1. Project Overview

Hifadhi is an **AI-powered agricultural risk management platform** for Kenyan SACCOs
(cooperative lending societies). The core data hierarchy is:

```
SACCO
 └── Farmer  (has a user account, linked to one SACCO)
      └── Farm  (GPS-validated Kenyan parcel)
           └── Season  (crop cycle with status machine)
                └── Loan  (credit line with status machine + risk score)
```

### User Roles

| Role | What they can do |
|---|---|
| `admin` | Full access to everything across all SACCOs. |
| `sacco_admin` | Read/write their own SACCO's data only. Cannot touch another SACCO. |
| `farmer` | Read-only access to their own farmer profile via `GET /farmers/{id}`. |
| `extension_officer` | Defined but not yet wired to any endpoint. Treat as unauthenticated for now. |

The authenticated user object (returned on login and from `/auth/me`) always includes a `role`
field. Build every conditional UI element off this field.

---

## 2. Authentication

### How auth works

- The API uses **JWT Bearer tokens** (HS256, default TTL = 24 hours).
- After login, store the token and attach it to **every** subsequent request:
  ```
  Authorization: Bearer <access_token>
  ```
- If the token is missing/expired, the server returns `401`.
- If the token is valid but the role is wrong, the server returns `403`.

---

### `POST /api/v1/auth/login`

**Purpose:** Exchange credentials for a bearer token.  
**Auth required:** No  
**Component hint:** `<LoginPage />` — email + password form.

#### Request body

```json
{
  "email": "admin26@gmail.com",
  "password": "admin26"
}
```

| Field | Type | Rules |
|---|---|---|
| `email` | `string` | Required, 1–255 chars |
| `password` | `string` | Required, min 1 char |

#### Success response `200`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "admin26@gmail.com",
    "role": "admin",
    "sacco_id": null,
    "farmer_id": null
  }
}
```

> `sacco_id` is set for `sacco_admin` users.  
> `farmer_id` is set for `farmer` users.  
> Both are `null` for `admin`.

#### Seeded credentials (for development)

| Email | Password | Role |
|---|---|---|
| `admin26@gmail.com` | `admin26` | `admin` |
| `saccoadmin26@gmail.com` | `saccoadmin26` | `sacco_admin` |

---

### `GET /api/v1/auth/me`

**Purpose:** Return the currently authenticated user. Use on app boot to restore session.  
**Auth required:** Yes (any role)  
**Component hint:** Call on mount, store in global auth context.

#### Success response `200`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "admin26@gmail.com",
  "role": "admin",
  "sacco_id": null,
  "farmer_id": null
}
```

---

## 3. Health Check

### `GET /health`

**Purpose:** Server liveness probe.  
**Auth required:** No  
**Component hint:** Display a status badge in an `<AppShell />` header or on a settings page.

#### Success response `200`

```json
{ "status": "ok" }
```

---

## 4. SACCOs

> **All SACCO endpoints require the `admin` role.**

A SACCO is the top-level organisational unit. Every farmer, farm, season, and loan belongs to
one. Creating a SACCO also automatically provisions a `sacco_admin` user account for it.

---

### `POST /api/v1/saccos`

**Purpose:** Create a new SACCO and its admin account.  
**Auth required:** `admin`  
**Component hint:** `<CreateSaccoModal />` or `<CreateSaccoPage />`

#### Request body

```json
{
  "name": "Kilimo SACCO",
  "county": "Nakuru",
  "admin_email": "admin@kilimo.co.ke",
  "admin_password": "securepassword"
}
```

| Field | Type | Rules |
|---|---|---|
| `name` | `string` | Required, 1–255 chars, must not be blank |
| `county` | `string \| null` | Optional, max 100 chars |
| `admin_email` | `string` | Required, 1–255 chars, must not be blank |
| `admin_password` | `string` | Required, 1–255 chars, must not be blank |

#### Success response `201`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Kilimo SACCO",
  "county": "Nakuru",
  "created_at": "2025-03-01T10:00:00Z"
}
```

---

### `GET /api/v1/saccos`

**Purpose:** List all SACCOs (paginated).  
**Auth required:** `admin`  
**Component hint:** `<SaccoListPage />` — table with pagination controls.

#### Query parameters

| Param | Type | Default | Rules |
|---|---|---|---|
| `offset` | `integer` | `0` | ≥ 0 |
| `limit` | `integer` | `20` | 1–100 |

#### Success response `200`

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Kilimo SACCO",
    "county": "Nakuru",
    "created_at": "2025-03-01T10:00:00Z"
  }
]
```

---

### `GET /api/v1/saccos/{sacco_id}`

**Purpose:** Fetch a single SACCO by its UUID.  
**Auth required:** `admin`  
**Component hint:** `<SaccoDetailPage />` — summary card + nested list of farmers.

#### Path parameter

| Param | Type |
|---|---|
| `sacco_id` | UUID string |

#### Success response `200`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Kilimo SACCO",
  "county": "Nakuru",
  "created_at": "2025-03-01T10:00:00Z"
}
```

---

## 5. Farmers

A farmer is a person belonging to a SACCO. Creating a farmer also provisions a `farmer` role user account for them.

- **`admin`** — can register and view any farmer.
- **`sacco_admin`** — can register and view farmers in their own SACCO only.
- **`farmer`** — can only view their own profile via `GET /farmers/{farmer_id}`.

---

### `POST /api/v1/farmers`

**Purpose:** Register a farmer and create their login credentials.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<RegisterFarmerModal />` or `<RegisterFarmerPage />`

#### Request body

```json
{
  "sacco_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "first_name": "Jane",
  "last_name": "Wanjiku",
  "phone": "+254712345678",
  "national_id": "12345678",
  "login_email": "jane@hifadhi.local",
  "login_password": "securepassword"
}
```

| Field | Type | Rules |
|---|---|---|
| `sacco_id` | UUID | Required. Must be an existing SACCO. `sacco_admin` must pass their own SACCO's ID. |
| `first_name` | `string` | Required, 1–100 chars, must not be blank |
| `last_name` | `string` | Required, 1–100 chars, must not be blank |
| `phone` | `string` | Required, 7–20 chars, digits only (optional leading `+`), cannot be all zeros |
| `national_id` | `string \| null` | Optional, max 20 chars, digits only, cannot be all zeros |
| `login_email` | `string` | Required, 1–255 chars, unique across the system |
| `login_password` | `string` | Required, 1–255 chars |

> **Conflict rules:** Duplicate `phone`, `national_id`, or `login_email` returns `409 Conflict`.

#### Success response `201`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sacco_id": "aaaa...",
  "first_name": "Jane",
  "last_name": "Wanjiku",
  "phone": "+254712345678",
  "national_id": "12345678",
  "created_at": "2025-03-01T10:00:00Z"
}
```

---

### `GET /api/v1/farmers/{farmer_id}`

**Purpose:** Fetch a farmer's full profile — includes their farms and all loans.  
**Auth required:** `admin`, owning `sacco_admin`, or the farmer themselves  
**Component hint:** `<FarmerProfilePage />` — summary + two sub-lists (Farms, Loans)

#### Path parameter

| Param | Type |
|---|---|
| `farmer_id` | UUID string |

#### Success response `200` — FarmerProfile composite

```json
{
  "farmer": {
    "id": "3fa85f64-...",
    "sacco_id": "aaaa...",
    "first_name": "Jane",
    "last_name": "Wanjiku",
    "phone": "+254712345678",
    "national_id": "12345678",
    "created_at": "2025-03-01T10:00:00Z"
  },
  "farms": [
    {
      "id": "bbbb...",
      "farmer_id": "3fa85f64-...",
      "name": "Wanjiku Maize Farm",
      "county": "Nakuru",
      "acreage": "2.50",
      "latitude": -0.30,
      "longitude": 36.10,
      "created_at": "2025-03-02T08:00:00Z"
    }
  ],
  "loans": [
    {
      "id": "cccc...",
      "farmer_id": "3fa85f64-...",
      "amount": "120000.00",
      "status": "active",
      "risk_score": 40,
      "created_at": "2025-03-05T09:00:00Z"
    }
  ]
}
```

> `risk_score` is `null` until a risk calculation has been run on the loan.

---

## 6. Farms

All farm endpoints require `admin` or `sacco_admin`. The `farmer` role **cannot** create farms.

---

### `POST /api/v1/farms`

**Purpose:** Create a farm parcel for a farmer.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<AddFarmModal />` or `<CreateFarmPage />` — include a map picker for lat/lon.

#### Request body

```json
{
  "farmer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Wanjiku Maize Farm",
  "county": "Nakuru",
  "acreage": "2.50",
  "latitude": -0.30,
  "longitude": 36.10
}
```

| Field | Type | Rules |
|---|---|---|
| `farmer_id` | UUID | Required. Must belong to an existing farmer. |
| `name` | `string` | Required, 1–255 chars, must not be blank |
| `county` | `string` | Required, 1–100 chars, must not be blank |
| `acreage` | `decimal` | Required, > 0, max 2 decimal places |
| `latitude` | `float` | Required, **-5.0 to 5.0** (Kenya bounding box) |
| `longitude` | `float` | Required, **33.5 to 42.0** (Kenya bounding box) |

> Coordinates outside Kenya's bounding box return `422`.

#### Success response `201`

```json
{
  "id": "bbbb...",
  "farmer_id": "3fa85f64-...",
  "name": "Wanjiku Maize Farm",
  "county": "Nakuru",
  "acreage": "2.50",
  "latitude": -0.30,
  "longitude": 36.10,
  "created_at": "2025-03-02T08:00:00Z"
}
```

---

### `GET /api/v1/farms/{farm_id}`

**Purpose:** Fetch a single farm by UUID.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<FarmDetailPage />` — map view + season list.

#### Success response `200`

Same shape as the farm object in the farms array above.

---

## 7. Seasons

A season represents one crop cycle on a farm. It has a **strict status machine**:

```
planned  →  active  →  harvested  (terminal — cannot exit)
                    →  failed     (terminal — cannot exit)
```

All season endpoints require `admin` or `sacco_admin`.

---

### `POST /api/v1/seasons`

**Purpose:** Create a new season for a farm. Always starts as `planned`.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<StartSeasonModal />` on the farm detail page.

#### Request body

```json
{
  "farm_id": "bbbb...",
  "crop_type": "Maize",
  "planting_date": "2025-03-01",
  "expected_harvest_date": "2025-07-01"
}
```

| Field | Type | Rules |
|---|---|---|
| `farm_id` | UUID | Required. Must be an existing farm. |
| `crop_type` | `string` | Required, 1–100 chars, must not be blank |
| `planting_date` | `date` (`YYYY-MM-DD`) | Required |
| `expected_harvest_date` | `date` (`YYYY-MM-DD`) | Required, **must be after `planting_date`** |

#### Success response `201`

```json
{
  "id": "dddd...",
  "farm_id": "bbbb...",
  "crop_type": "Maize",
  "planting_date": "2025-03-01",
  "expected_harvest_date": "2025-07-01",
  "status": "planned",
  "created_at": "2025-02-28T12:00:00Z"
}
```

---

### `GET /api/v1/seasons/{season_id}`

**Purpose:** Fetch a single season.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<SeasonDetailPage />` — status badge + dates + linked loans.

#### Success response `200`

Same shape as the season object above.

---

### `PATCH /api/v1/seasons/{season_id}/activate`

**Purpose:** Transition season from `planned` → `active`.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<ActivateSeasonButton />` — only show when `status === "planned"`.

**No request body.**

#### Success response `200` — updated season object

```json
{
  "id": "dddd...",
  "status": "active",
  ...
}
```

> Returns `422` if the season is not currently `planned`.

---

### `PATCH /api/v1/seasons/{season_id}/harvest`

**Purpose:** Transition season from `active` → `harvested` (terminal).  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<MarkHarvestedButton />` — only show when `status === "active"`.

**No request body.**

#### Success response `200` — updated season object with `"status": "harvested"`

---

### `PATCH /api/v1/seasons/{season_id}/fail`

**Purpose:** Transition season from `active` → `failed` (terminal).  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<MarkFailedButton />` — only show when `status === "active"`, styled as a destructive action.

**No request body.**

#### Success response `200` — updated season object with `"status": "failed"`

> A `failed` season increases the linked loan's risk score by **+40 points** when risk is calculated.

---

## 8. Loans

A loan has a **strict status machine**:

```
pending → approved  → disbursed → active → repaid     (terminal)
        → rejected  (terminal)           → defaulted  (terminal)
        ↑
  approved → rejected  (terminal)
```

All loan endpoints require `admin` or `sacco_admin`.

---

### `POST /api/v1/loans`

**Purpose:** Create a loan for a farmer. Always starts as `pending`.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<CreateLoanModal />` on the farmer profile page.

#### Request body

```json
{
  "farmer_id": "3fa85f64-...",
  "amount": "120000.00",
  "season_id": "dddd..."
}
```

| Field | Type | Rules |
|---|---|---|
| `farmer_id` | UUID | Required. Must be an existing farmer. |
| `amount` | `decimal` | Required, > 0, max 2 decimal places |
| `season_id` | UUID \| null | Optional but strongly recommended for accurate risk scoring |

#### Success response `201`

```json
{
  "id": "cccc...",
  "farmer_id": "3fa85f64-...",
  "amount": "120000.00",
  "status": "pending",
  "risk_score": null,
  "created_at": "2025-03-05T09:00:00Z"
}
```

---

### `GET /api/v1/loans/{loan_id}`

**Purpose:** Fetch a single loan.  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<LoanDetailPage />` — status badge, amount, risk score card, action buttons.

#### Success response `200` — LoanRead object

---

### Status transition endpoints

All take the path parameter `loan_id` (UUID), require **no request body**, and return the updated `LoanRead` object on `200`.

| Endpoint | Transition | Show button when | Styled as |
|---|---|---|---|
| `PATCH /api/v1/loans/{id}/approve` | `pending → approved` | `status === "pending"` | Primary action |
| `PATCH /api/v1/loans/{id}/reject` | `pending\|approved → rejected` | `status === "pending"` or `status === "approved"` | Destructive |
| `PATCH /api/v1/loans/{id}/disburse` | `approved → disbursed` | `status === "approved"` | Primary action |
| `PATCH /api/v1/loans/{id}/activate` | `disbursed → active` | `status === "disbursed"` | Primary action |
| `PATCH /api/v1/loans/{id}/repay` | `active → repaid` | `status === "active"` | Success/green |
| `PATCH /api/v1/loans/{id}/default` | `active → defaulted` | `status === "active"` | Destructive |

> Invalid transitions return `422`. Terminal states (`repaid`, `defaulted`, `rejected`) show no action buttons.

---

### `GET /api/v1/loans/{loan_id}/risk`

**Purpose:** Compute and return a risk score for a loan (reads/calculates in real time).  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<RiskScoreCard />` — score gauge, category badge, trigger button.

#### Query parameter (optional)

| Param | Type | Description |
|---|---|---|
| `season_id` | UUID | If provided, factors the season's status into scoring |

Example: `GET /api/v1/loans/cccc.../risk?season_id=dddd...`

#### Success response `200`

```json
{
  "loan_id": "cccc...",
  "score": 40,
  "category": "medium"
}
```

| Field | Type | Values |
|---|---|---|
| `loan_id` | UUID | ID of the scored loan |
| `score` | `integer` | 0–100 |
| `category` | `string` | `"low"` (0–30), `"medium"` (31–60), `"high"` (61–100) |

---

### `POST /api/v1/loans/{loan_id}/risk/recalculate`

**Purpose:** Force a fresh risk recalculation (same logic as GET, useful for refresh buttons).  
**Auth required:** `admin` or `sacco_admin`  
**Component hint:** `<RecalculateRiskButton />` inside `<RiskScoreCard />`.

**No request body.** Same optional `?season_id=<uuid>` query param. Same `200` response shape as above.

---

## 9. Error Responses

All errors follow this shape:

```json
{ "detail": "Human-readable error message." }
```

| HTTP status | When it happens | UI behaviour |
|---|---|---|
| `401` | Missing/expired/invalid bearer token | Redirect to login page, clear stored token |
| `403` | Valid token but wrong role or wrong SACCO scope | Show a "Permission denied" toast/banner |
| `404` | Resource ID doesn't exist in the database | Show a "Not found" empty state |
| `409` | Duplicate phone/national_id/email, or DB constraint conflict | Show the `detail` message inline under the form field |
| `422` | Validation error or illegal status transition | Show the `detail` message inline; for transitions, hide/disable the action button |

---

## 10. Global State & Session Management

### What to persist

| Key | Value | Where |
|---|---|---|
| `auth.token` | JWT string | `localStorage` or `sessionStorage` |
| `auth.user` | `UserRead` object | In-memory (re-fetch on reload via `/auth/me`) |

### Auth flow

1. On app load, check for a stored token.
2. If token exists → call `GET /auth/me`. If `200`, restore session. If `401`, clear token and redirect to login.
3. On login success → store token and user, redirect based on role (see below).
4. On logout → clear token and user, redirect to `/login`.

### Role-based redirect after login

| Role | Redirect to |
|---|---|
| `admin` | `/dashboard` or `/saccos` (list of all SACCOs) |
| `sacco_admin` | `/saccos/{sacco_id}` (their own SACCO detail page) |
| `farmer` | `/farmers/{farmer_id}` (their own profile) |

---

## 11. Suggested Page & Component Map

```
/login                        → <LoginPage />
/dashboard                    → <DashboardPage />         (admin only)
/saccos                       → <SaccoListPage />         (admin only)
/saccos/new                   → <CreateSaccoPage />       (admin only)
/saccos/:saccoId              → <SaccoDetailPage />       (admin only)

/farmers/new                  → <RegisterFarmerPage />    (admin, sacco_admin)
/farmers/:farmerId            → <FarmerProfilePage />     (admin, sacco_admin, farmer-self)

/farms/new                    → <CreateFarmPage />        (admin, sacco_admin)
/farms/:farmId                → <FarmDetailPage />        (admin, sacco_admin)

/seasons/new                  → <StartSeasonPage />       (admin, sacco_admin)
/seasons/:seasonId            → <SeasonDetailPage />      (admin, sacco_admin)

/loans/new                    → <CreateLoanPage />        (admin, sacco_admin)
/loans/:loanId                → <LoanDetailPage />        (admin, sacco_admin)
  └── /loans/:loanId/risk     → embedded <RiskScoreCard />
```

### Shared components

| Component | Used in |
|---|---|
| `<StatusBadge status />` | LoanDetailPage, SeasonDetailPage, FarmerProfilePage |
| `<RiskScoreCard />` | LoanDetailPage |
| `<ActionButton label onClick disabled />` | All status-transition buttons |
| `<ErrorBanner message />` | All pages — show API `detail` field |
| `<ConfirmModal />` | Destructive actions: reject, default, fail |
| `<Pagination offset limit total onChange />` | SaccoListPage |
| `<MapPicker onCoordinateChange />` | CreateFarmPage — lat/lon with Kenya bounding box |

---

## 12. Validation Rules Cheat Sheet

| Field | Rules |
|---|---|
| `phone` | Digits only, optional leading `+`, 7–20 chars, not all zeros |
| `national_id` | Digits only, max 20 chars, not all zeros (optional) |
| `latitude` | Float, -5.0 to 5.0 (Kenya) |
| `longitude` | Float, 33.5 to 42.0 (Kenya) |
| `acreage` | Decimal > 0, 2 decimal places |
| `amount` | Decimal > 0, 2 decimal places |
| `expected_harvest_date` | Must be strictly after `planting_date` |
| `crop_type`, `name`, `county`, `first_name`, `last_name` | Must not be blank/whitespace-only |
| `sacco_admin` assigning `sacco_id` | Must equal their own `sacco_id` or the API returns `403` |

---

## 13. Risk Score Logic (for UI display)

The risk engine runs serverside. The frontend just displays the returned score and category.

| Condition | Points added |
|---|---|
| Linked season status is `failed` | +40 |
| Weather alert (Phase 2, not yet live) | +15 |
| Missed recommendation (Phase 2, not yet live) | +20 |

| Score range | Category | Suggested colour |
|---|---|---|
| 0–30 | `low` | Green |
| 31–60 | `medium` | Amber/Orange |
| 61–100 | `high` | Red |

Score is capped at 100. `risk_score` on a `LoanRead` is `null` until at least one risk calculation
has been run.
