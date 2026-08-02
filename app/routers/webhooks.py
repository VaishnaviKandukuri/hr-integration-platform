from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ATSWebhookEnvelope
from app.models.db_models import WebhookEvent, Employee
from app.services.transform import transform_to_employee

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/ats")
def receive_ats_webhook(envelope: ATSWebhookEnvelope, db: Session = Depends(get_db)):
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

        employee.employment_status = "active"
        employee.hire_date = envelope.data.employment_info.hire_date
        employee.department = envelope.data.employment_info.department
        employee.job_title = envelope.data.employment_info.job_title

        result_status = "rehired"

    else:
        employee = transform_to_employee(envelope)

        db.add(employee)
        db.flush()
        result_status = "accepted"

    webhook_event = WebhookEvent(
        event_id=envelope.event_id,
        event_type=envelope.event_type,
        employee_id=employee.id,
        raw_payload=envelope.model_dump_json(),
    )
    db.add(webhook_event)

    db.commit()
    db.refresh(employee)

    return {
        "status": result_status,
        "employee_id": employee.id,
        "event_id": envelope.event_id,
    }