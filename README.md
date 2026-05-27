# Kudos System — Minimal MVP

This repository contains a minimal, runnable MVP of the Kudos system described in [SPECIFICATION.md](SPECIFICATION.md).

What this MVP includes:
- A tiny Flask-based API: `apps/api/app.py` (SQLite-backed).
- A simple static frontend: `apps/web/index.html` that calls the API.

What is intentionally out of scope for this MVP:
- Production authentication (the API uses a simple header-based admin key for moderation endpoints).
- Deployment and database migrations.

Getting started (local development)

1. Create and activate a Python virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install API dependencies:

```powershell
pip install -r apps/api/requirements.txt
```

3. Run the API server:

```powershell
python apps/api/app.py
```

4. Open the frontend in your browser:

Open `apps/web/index.html` directly (it calls the local API at `http://127.0.0.1:5000`).

Migrations

This project includes a minimal SQL-based migrations system under `apps/api/migrations`.
Apply migrations with:

```powershell
python apps/api/migrate.py
```

Tests

Run the API tests (uses `pytest`):

```powershell
python -m pytest apps/api/tests
```

Frontend (React)

The frontend is now a minimal Vite + React app in `apps/web`.
Install dependencies and run the dev server:

```powershell
cd apps/web
npm install
npm run dev
```

Notes

- For moderation/admin endpoints use the API login to obtain a JWT. Call `POST /api/auth/login` with `{"email":"bob@example.com"}` and use the returned `access_token` in the `Authorization: Bearer <token>` header.
- For local testing the JWT secret is `dev-jwt-secret`. Replace it in production.
 - For moderation/admin endpoints use the API login to obtain a JWT. Call `POST /api/auth/login` with `{"email":"bob@example.com"}` and use the returned `access_token` in the `Authorization: Bearer <token>` header.
 - Secrets: set a strong secret in the environment variable `KUDOS_JWT_SECRET` before running the API in production. Example (PowerShell):

```powershell
$env:KUDOS_JWT_SECRET = 'REPLACE_WITH_A_LONG_RANDOM_SECRET'
```

Repository cleanup: if there are SQLite DB files committed (e.g., `apps/api/kudos.db`), remove them from the repository history and keep only SQL migration scripts. To remove tracked DB files now:

```powershell
git rm --cached apps/api/kudos.db || true
git rm --cached apps/api/kudos_test_debug.db || true
git commit -m "Remove DB artifacts from repo" || true
git push
```

Continuous Integration

A minimal GitHub Actions workflow is included to run tests and build the frontend. The workflow file is at `.github/workflows/ci.yml`.

Admin moderation (MVP): use the header `X-Admin-Key: admin-secret` for `/api/admin/...` endpoints.

Notes on repository hygiene

- Unwanted binary files such as `*.pptx`, `*.exe`, etc. are ignored by `.gitignore` and should not be committed.
- If there are already large/binary files in the repo, they should be removed from Git history separately (not performed automatically by this MVP patch).

Next steps (suggested)

- Add proper authentication (SSO) and role-based authorization.
- Add database migrations and deploy scripts.
- Replace the static frontend with a React app as described in the spec.

Enjoy the MVP — run the API, open the frontend, and try sending kudos!
