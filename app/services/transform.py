from decimal import Decimal
from app.models.schemas import ATSWebhookEnvelope
from app.models.db_models import Employee
from app.services.pii import mask_email, mask_phone, last4_national_id


def transform_to_employee(envelope: ATSWebhookEnvelope) -> Employee:
    candidate = envelope.data

    employee = Employee(
        first_name=candidate.personal_info.first_name,
        last_name=candidate.personal_info.last_name,
        email_masked=mask_email(candidate.personal_info.email),
        phone_masked=mask_phone(candidate.personal_info.phone) if candidate.personal_info.phone else None,
        national_id_last4=last4_national_id(candidate.personal_info.national_id) if candidate.personal_info.national_id else None,
        department=candidate.employment_info.department,
        job_title=candidate.employment_info.job_title,
        base_salary=Decimal(str(candidate.compensation.base_salary)),
        currency=candidate.compensation.currency,
        hire_date=candidate.employment_info.hire_date,
    )

    return employee