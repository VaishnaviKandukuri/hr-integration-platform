import time
import json
import requests
from app.core.security import compute_signature
from app.config import settings

payload = {
    "event_id": "evt_020",
    "event_type": "employee.hired",
    "triggered_at": "2026-08-02T12:00:00",
    "data": {
        "ats_candidate_id": "cand_signed_001",
        "personal_info": {
            "first_name": "Signed",
            "last_name": "Request",
            "email": "signed.request@company.com",
        },
        "employment_info": {
            "department": "Engineering",
            "job_title": "Integration Engineer",
            "employment_type": "full_time",
            "hire_date": "2026-08-02",
        },
        "compensation": {
            "base_salary": 80000,
        },
    },
}

body_bytes = json.dumps(payload).encode()
timestamp = str(int(time.time()))
signature = compute_signature(body_bytes, timestamp, settings.WEBHOOK_SIGNING_SECRET)

response = requests.post(
    "http://127.0.0.1:8000/webhooks/ats",
    data=body_bytes,
    headers={
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Timestamp": timestamp,
    },
)

print("Status code:", response.status_code)
print("Response body:", response.json())