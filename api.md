# AgroForesight API Routes

Base URL: `http://127.0.0.1:8000`

## Authentication

Login-only access. All protected routes expect a bearer token from `POST /api/v1/auth/login`.

- `POST /api/v1/auth/login` - login and receive a bearer token.
- `GET /api/v1/auth/me` - inspect the current user.

Seeded demo users:

- `admin26@gmail.com` / `admin26` - `admin`
- `saccoadmin26@gmail.com` / `saccoadmin26` - `sacco_admin`

Protected routes expect the bearer token in the `Authorization` header.

Role access summary:

- `admin` - full access.
- `sacco_admin` - access to their own SACCO scope.
- `farmer` - access to their own farmer profile only.

## Health

- `GET /health` - health check.

## Saccos

- `POST /api/v1/saccos` - create a sacco and provision its sacco admin. Requires `admin`.
- `GET /api/v1/saccos` - list saccos. Requires `admin`.
- `GET /api/v1/saccos/{sacco_id}` - fetch one sacco. Requires `admin`.

## Farmers

- `POST /api/v1/farmers` - register a farmer and provision the farmer login. Requires `admin` or `sacco_admin` for the same SACCO.
- `GET /api/v1/farmers/{farmer_id}` - fetch a farmer profile with farms and loans. Requires `admin`, the owning `sacco_admin`, or the farmer themselves.

## Farms

- `POST /api/v1/farms` - create a farm. Requires `admin` or the owning `sacco_admin`.
- `GET /api/v1/farms/{farm_id}` - fetch one farm. Requires `admin` or the owning `sacco_admin`.

## Seasons

- `POST /api/v1/seasons` - create a season. Requires `admin` or the owning `sacco_admin`.
- `GET /api/v1/seasons/{season_id}` - fetch one season. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/seasons/{season_id}/activate` - activate a season. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/seasons/{season_id}/harvest` - mark a season harvested. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/seasons/{season_id}/fail` - mark a season failed. Requires `admin` or the owning `sacco_admin`.

## Loans

- `POST /api/v1/loans` - create a loan. Requires `admin` or the owning `sacco_admin`.
- `GET /api/v1/loans/{loan_id}` - fetch one loan. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/approve` - approve a loan. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/reject` - reject a loan. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/disburse` - disburse a loan. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/activate` - activate a loan. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/repay` - mark a loan repaid. Requires `admin` or the owning `sacco_admin`.
- `PATCH /api/v1/loans/{loan_id}/default` - mark a loan defaulted. Requires `admin` or the owning `sacco_admin`.
- `GET /api/v1/loans/{loan_id}/risk` - calculate risk, optionally with `season_id`. Requires `admin` or the owning `sacco_admin`.
- `POST /api/v1/loans/{loan_id}/risk/recalculate` - recalculate risk, optionally with `season_id`. Requires `admin` or the owning `sacco_admin`.
