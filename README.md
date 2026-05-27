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

Admin moderation (MVP): use the header `X-Admin-Key: admin-secret` for `/api/admin/...` endpoints.

Notes on repository hygiene

- Unwanted binary files such as `*.pptx`, `*.exe`, etc. are ignored by `.gitignore` and should not be committed.
- If there are already large/binary files in the repo, they should be removed from Git history separately (not performed automatically by this MVP patch).

Next steps (suggested)

- Add proper authentication (SSO) and role-based authorization.
- Add database migrations and deploy scripts.
- Replace the static frontend with a React app as described in the spec.

Enjoy the MVP — run the API, open the frontend, and try sending kudos!
