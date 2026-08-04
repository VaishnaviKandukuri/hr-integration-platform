from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ATSWebhookEnvelope
from app.models.db_models import WebhookEvent, Employee
from app.services.transform import transform_to_employee
from app.services.audit import log_employee_change, _employee_to_dict
from app.core.security import require_valid_signature
import json
from app.services.pii import mask_payload_for_storage

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/ats")
def receive_ats_webhook(envelope: ATSWebhookEnvelope, db: Session = Depends(get_db), verified_raw_body: bytes = Depends(require_valid_signature),):
    existing_event = db.query(WebhookEvent).filter(
        WebhookEvent.event_id == envelope.event_id
    ).first()

    if existing_event:
        return {
            "status": "duplicate",
            "employee_id": existing_event.employee_id,
            "event_id": envelope.event_id,
            "message": "This event_id was already processed. No new record created.",
        }

    if envelope.data.employment_info.is_rehire:
        previous_number = envelope.data.employment_info.previous_employee_number

        if not previous_number:
            raise HTTPException(
                status_code=422,
                detail="is_rehire=True but previous_employee_number was not provided.",
            )

        employee = db.query(Employee).filter(
            Employee.employee_number == previous_number
        ).first()

        if not employee:
            raise HTTPException(
                status_code=404,
                detail=f"Rehire event references previous_employee_number '{previous_number}', but no matching employee was found.",
            )

        before_snapshot = _employee_to_dict(employee)

        employee.employment_status = "active"
        employee.hire_date = envelope.data.employment_info.hire_date
        employee.department = envelope.data.employment_info.department
        employee.job_title = envelope.data.employment_info.job_title

        result_status = "rehired"
        log_employee_change(db, employee, action="rehire", actor="MockATS-webhook", before_snapshot=before_snapshot)

    else:
        employee = transform_to_employee(envelope)

        db.add(employee)
        db.flush()
        result_status = "accepted"
        log_employee_change(db, employee, action="create", actor="MockATS-webhook")

    webhook_event = WebhookEvent(
        event_id=envelope.event_id,
        event_type=envelope.event_type,
        employee_id=employee.id,
        raw_payload=json.dumps(mask_payload_for_storage(envelope.model_dump(mode="json"))),
    )
    db.add(webhook_event)

    db.commit()
    db.refresh(employee)

    return {
        "status": result_status,
        "employee_id": employee.id,
        "event_id": envelope.event_id,
    }