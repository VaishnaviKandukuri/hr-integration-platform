# HR Integration & Data Governance Platform

A FastAPI service simulating a real-world HR-tech integration: a mock ATS sends signed webhooks for hire/rehire events, which are authenticated, validated, transformed, PII-masked, and written into a canonical employee record — with full audit logging and a legacy-system XML export for payroll.

Built as a focused portfolio project targeting HR-tech data + integrations roles, prioritizing integration engineering (auth, idempotency, data governance) over ML/analytics.

## Architecture

**Write path:** Mock ATS → HMAC signature verification → duplicate/rehire business logic → PII masking + transform → single atomic transaction (Employee + WebhookEvent + AuditLog).

**Read path:** Client → OAuth2 Client Credentials token → RBAC scope check (`payroll:read`) → JSON (`GET /employees/{id}`) or legacy XML (`GET /payroll/employees/{id}/export.xml`).

## What's implemented

- **Nested webhook payload schema** (Pydantic) modeled on real ATS webhook shapes
- **Dynamic test data generation**: `scripts/send_test_webhook.py` uses Faker to generate realistic, varied employee data on every run, rather than a fixed hardcoded fixture
- **HMAC-SHA256 signature verification** with replay-attack protection (timestamp tolerance window, constant-time comparison)
- **OAuth2 Client Credentials flow** with JWT issuance and RBAC scopes
- **Idempotency**: duplicate `event_id` detection via a dedicated ledger table, backed by a database-level unique constraint
- **Rehire handling**: matches and reactivates existing employee records instead of creating duplicates, via `previous_employee_number`
- **PII masking**: email/phone masked, national ID reduced to last 4 digits, applied before any database write
- **Audit logging**: before/after snapshots on every create/rehire, with actor and timestamp
- **JSON → XML export** for a legacy payroll-style consumer
- **Automated tests** (pytest) covering hire, duplicate detection, rehire, and signature rejection
- **CI/CD**: GitHub Actions runs the full pytest suite on every push to `main`, using GitHub Secrets for configuration (no hardcoded values, no `.env` committed)
- **Security hardening**: constant-time credential comparison, no hardcoded client secrets, PII masking applied to both the primary employee record and the raw webhook audit trail
- **Batch export pattern**: CSV batch export of active employees (`scripts/batch_export.py`), alongside the real-time webhook pattern — with a documented (not executed) SFTP upload implementation for a live legacy-payroll target


## Tech stack

**Core:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite
**Auth/Security:** python-jose (JWT), python-multipart, hmac/hashlib (stdlib)
**Testing:** pytest, httpx (via FastAPI TestClient)
**Data generation:** Faker
**Integration patterns:** paramiko (SFTP, pattern demonstrated not executed), csv (stdlib, batch export), xml.etree.ElementTree (stdlib, legacy XML export)
**CI/CD:** GitHub Actions
**Containerization:** Docker (written, not locally run)


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

