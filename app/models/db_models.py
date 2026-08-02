import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, Integer, Text
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, default=generate_uuid)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email_masked = Column(String, nullable=False)
    phone_masked = Column(String, nullable=True)
    national_id_last4 = Column(String, nullable=True)

    department = Column(String, nullable=False)
    job_title = Column(String, nullable=False)

    base_salary = Column(Numeric(12, 2), nullable=True)
    currency = Column(String, default="INR")

    employment_status = Column(String, default="active")
    hire_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    processing_status = Column(String, default="processed")
    employee_id = Column(String, nullable=True)
    raw_payload = Column(Text, nullable=True)
    received_at = Column(DateTime, default=dt.datetime.utcnow)
