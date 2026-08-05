import time
import json
import uuid
import random
import requests
from faker import Faker
from app.core.security import compute_signature
from app.config import settings

fake = Faker()

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "Operations", "Platform Engineering"]
JOB_TITLES = ["Software Engineer", "Account Executive", "Marketing Manager", "Financial Analyst", "Operations Lead"]

payload = {
    "event_id": f"evt_{uuid.uuid4().hex[:8]}",
    "event_type": "employee.hired",
    "triggered_at": "2026-08-05T10:00:00",
    "data": {
        "ats_candidate_id": f"cand_{uuid.uuid4().hex[:8]}",
        "personal_info": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.company_email(),
            "phone": fake.msisdn()[:10],
        },
        "employment_info": {
            "department": random.choice(DEPARTMENTS),
            "job_title": random.choice(JOB_TITLES),
            "employment_type": "full_time",
            "hire_date": "2026-08-05",
        },
        "compensation": {
            "base_salary": random.randint(400000, 1800000),
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