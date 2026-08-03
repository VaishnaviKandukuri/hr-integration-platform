import time
import json
from app.core.security import compute_signature
from app.config import settings


def build_signed_request(payload: dict):
    body_bytes = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    signature = compute_signature(body_bytes, timestamp, settings.WEBHOOK_SIGNING_SECRET)
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Timestamp": timestamp,
    }
    return body_bytes, headers


def make_hire_payload(event_id: str, candidate_id: str) -> dict:
    return {
        "event_id": event_id,
        "event_type": "employee.hired",
        "triggered_at": "2026-08-03T10:00:00",
        "data": {
            "ats_candidate_id": candidate_id,
            "personal_info": {
                "first_name": "Test",
                "last_name": "Person",
                "email": f"{candidate_id}@company.com",
            },
            "employment_info": {
                "department": "Engineering",
                "job_title": "Engineer",
                "employment_type": "full_time",
                "hire_date": "2026-08-03",
            },
            "compensation": {"base_salary": 60000},
        },
    }


def test_new_hire_is_accepted(client):
    payload = make_hire_payload("test_evt_001", "test_cand_001")
    body, headers = build_signed_request(payload)

    response = client.post("/webhooks/ats", content=body, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_duplicate_event_id_is_rejected(client):
    payload = make_hire_payload("test_evt_002", "test_cand_002")
    body, headers = build_signed_request(payload)

    first_response = client.post("/webhooks/ats", content=body, headers=headers)
    second_response = client.post("/webhooks/ats", content=body, headers=headers)

    assert first_response.json()["status"] == "accepted"
    assert second_response.json()["status"] == "duplicate"
    assert first_response.json()["employee_id"] == second_response.json()["employee_id"]


def test_rehire_reactivates_existing_employee(client):
    hire_payload = make_hire_payload("test_evt_003", "test_cand_003")
    body, headers = build_signed_request(hire_payload)
    hire_response = client.post("/webhooks/ats", content=body, headers=headers)
    original_employee_id = hire_response.json()["employee_id"]

    rehire_payload = {
        "event_id": "test_evt_004",
        "event_type": "employee.rehired",
        "triggered_at": "2026-08-03T11:00:00",
        "data": {
            "ats_candidate_id": "test_cand_003_rehire",
            "personal_info": {
                "first_name": "Test",
                "last_name": "Person",
                "email": "test_cand_003@company.com",
            },
            "employment_info": {
                "department": "Platform",
                "job_title": "Senior Engineer",
                "employment_type": "full_time",
                "hire_date": "2026-08-03",
                "is_rehire": True,
                "previous_employee_number": "test_cand_003",
            },
            "compensation": {"base_salary": 90000},
        },
    }
    body2, headers2 = build_signed_request(rehire_payload)
    rehire_response = client.post("/webhooks/ats", content=body2, headers=headers2)

    assert rehire_response.status_code == 200
    assert rehire_response.json()["status"] == "rehired"
    assert rehire_response.json()["employee_id"] == original_employee_id


def test_invalid_signature_is_rejected(client):
    payload = make_hire_payload("test_evt_005", "test_cand_005")
    body, _ = build_signed_request(payload)

    bad_headers = {
        "Content-Type": "application/json",
        "X-Signature": "totally-wrong-signature",
        "X-Timestamp": str(int(time.time())),
    }
    response = client.post("/webhooks/ats", content=body, headers=bad_headers)

    assert response.status_code == 401