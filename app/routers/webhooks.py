from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ATSWebhookEnvelope
from app.services.transform import transform_to_employee

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/ats")
def receive_ats_webhook(envelope: ATSWebhookEnvelope, db: Session = Depends(get_db)):
    employee = transform_to_employee(envelope)

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "status": "accepted",
        "employee_id": employee.id,
        "event_id": envelope.event_id,
    }