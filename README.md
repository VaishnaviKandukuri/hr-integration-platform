# HR Integration & Data Governance Platform

A FastAPI service simulating a real-world HR-tech integration: a mock ATS sends signed webhooks for hire/rehire events, which are authenticated, validated, transformed, PII-masked, and written into a canonical employee record — with full audit logging and a legacy-system XML export for payroll.

Built as a focused portfolio project targeting HR-tech data + integrations roles, prioritizing integration engineering (auth, idempotency, data governance) over ML/analytics.

## Architecture

**Write path:** Mock ATS → HMAC signature verification → duplicate/rehire business logic → PII masking + transform → single atomic transaction (Employee + WebhookEvent + AuditLog).

**Read path:** Client → OAuth2 Client Credentials token → RBAC scope check (`payroll:read`) → JSON (`GET /employees/{id}`) or legacy XML (`GET /payroll/employees/{id}/export.xml`).

## What's implemented

- **Nested webhook payload schema** (Pydantic) modeled on real ATS webhook shapes
- **HMAC-SHA256 signature verification** with replay-attack protection (timestamp tolerance window, constant-time comparison)
- **OAuth2 Client Credentials flow** with JWT issuance and RBAC scopes
- **Idempotency**: duplicate `event_id` detection via a dedicated ledger table, backed by a database-level unique constraint
- **Rehire handling**: matches and reactivates existing employee records instead of creating duplicates, via `previous_employee_number`
- **PII masking**: email/phone masked, national ID reduced to last 4 digits, applied before any database write
- **Audit logging**: before/after snapshots on every create/rehire, with actor and timestamp
- **JSON → XML export** for a legacy payroll-style consumer
- **Automated tests** (pytest) covering hire, duplicate detection, rehire, and signature rejection

## Tech stack

Python, FastAPI, SQLAlchemy, Pydantic, SQLite, python-jose (JWT), pytest, Docker

## Running locally

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs. Note: `POST /webhooks/ats` requires a valid HMAC signature and cannot be tested via the docs UI directly — use `python -m scripts.send_test_webhook`.

## Running tests

```bash
pytest tests/ -v
```

## Roadmap / not yet built

- SSO/SAML (conceptually understood; not built — disproportionate scope for this project)
- Full iPaaS integration (Workato) — evaluated, deprioritized in favor of building the integration logic directly
- Alembic migrations (currently using `Base.metadata.create_all`, which cannot alter existing tables — a known, real limitation)
- Batch/SFTP-style sync alongside the current real-time webhook pattern
- Cloud event-driven pattern (e.g., one Lambda + SQS example)
- CI pipeline (GitHub Actions) running tests on push