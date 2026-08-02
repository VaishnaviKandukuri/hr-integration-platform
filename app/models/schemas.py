import datetime as dt
from typing import Literal

from pydantic import BaseModel, EmailStr


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    national_id: str | None = None

class EmploymentInfo(BaseModel):
    department: str
    job_title: str
    employment_type: Literal["full_time", "part_time", "contract", "intern"]
    hire_date: dt.date
    is_rehire: bool = False

class CompensationBlock(BaseModel):
    base_salary: float
    currency: str = "INR"
    pay_frequency: Literal["monthly", "annual", "biweekly"] = "monthly"


class ATSCandidateObject(BaseModel):
    ats_candidate_id: str
    personal_info: PersonalInfo
    employment_info: EmploymentInfo
    compensation: CompensationBlock


class ATSWebhookEnvelope(BaseModel):
    event_id: str
    event_type: Literal["employee.hired", "employee.rehired", "employee.updated"]
    triggered_at: dt.datetime
    data: ATSCandidateObject

class EmployeeOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email_masked: str
    phone_masked: str | None
    department: str
    job_title: str
    base_salary: float | None
    currency: str
    employment_status: str
    hire_date: dt.date

    class Config:
        from_attributes = True