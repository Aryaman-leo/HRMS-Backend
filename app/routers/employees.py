"""Routes for /api/employees. Delegates to controller."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import employee_controller
from app.database import get_db
from app.schemas import EmployeeCreate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return employee_controller.list_employees(db)


@router.post("", status_code=201, response_model=EmployeeResponse)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_controller.create_employee(body, db)


@router.delete("/{id_or_employee_id}", status_code=204)
def delete_employee(id_or_employee_id: str, db: Session = Depends(get_db)):
    return employee_controller.delete_employee(id_or_employee_id, db)
