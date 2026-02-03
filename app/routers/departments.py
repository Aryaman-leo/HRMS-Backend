"""Routes for /api/departments. Delegates to controller."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import department_controller
from app.database import get_db
from app.schemas import DepartmentCreate, DepartmentResponse, DepartmentWithEmployeesResponse

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentWithEmployeesResponse])
def list_departments(db: Session = Depends(get_db)):
    return department_controller.list_departments(db)


@router.post("", status_code=201, response_model=DepartmentResponse)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db)):
    return department_controller.create_department(body, db)


@router.delete("/{id}", status_code=204)
def delete_department(id: int, db: Session = Depends(get_db)):
    return department_controller.delete_department(id, db)
