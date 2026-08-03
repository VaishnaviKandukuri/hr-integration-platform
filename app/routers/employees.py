from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Employee
from app.models.schemas import EmployeeOut
from app.core.security import get_current_client, RequireScope

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: str, db: Session = Depends(get_db), current_client: str =  Depends(RequireScope("payroll:read")),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee