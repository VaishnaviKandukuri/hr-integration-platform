from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ATSWebhookEnvelope
from app.models.db_models import WebhookEvent
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

    employee = transform_to_employee(envelope)

    db.add(employee)
    db.flush()

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
        "status": "accepted",
        "employee_id": employee.id,
        "event_id": envelope.event_id,
    }