from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Employee
from app.services.xml_export import employee_to_xml
from app.core.security import RequireScope

router = APIRouter(prefix="/payroll", tags=["payroll"])


@router.get("/employees/{employee_id}/export.xml")
def export_employee_xml(
    employee_id: str,
    db: Session = Depends(get_db),
    current_client: str = Depends(RequireScope("payroll:read")),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    xml_content = employee_to_xml(employee)
    return Response(content=xml_content, media_type="application/xml")