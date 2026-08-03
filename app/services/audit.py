import json
from sqlalchemy.orm import Session
from app.models.db_models import AuditLog, Employee


def _employee_to_dict(employee: Employee) -> dict:
    return {
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email_masked": employee.email_masked,
        "department": employee.department,
        "job_title": employee.job_title,
        "base_salary": str(employee.base_salary) if employee.base_salary is not None else None,
        "employment_status": employee.employment_status,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
    }


def log_employee_change(
    db: Session,
    employee: Employee,
    action: str,
    actor: str,
    before_snapshot: dict | None = None,
) -> None:
    audit_entry = AuditLog(
        entity_type="Employee",
        entity_id=employee.id,
        action=action,
        actor=actor,
        before_state=json.dumps(before_snapshot) if before_snapshot else None,
        after_state=json.dumps(_employee_to_dict(employee)),
    )
    db.add(audit_entry)