"""Department controller: HTTP handling for department endpoints."""
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Department
from app.schemas import (
    BulkResult,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentWithEmployeesResponse,
    EmployeeSummary,
)
from app.services import department_service


def _department_with_employees_response(dept: Department) -> DepartmentWithEmployeesResponse:
    employees = [
        EmployeeSummary(
            id=emp.id,
            employee_id=emp.employee_id,
            full_name=emp.full_name,
            email=emp.email,
        )
        for emp in (dept.employees or [])
    ]
    return DepartmentWithEmployeesResponse(id=dept.id, name=dept.name, employees=employees)


def list_departments(db: Session) -> list[DepartmentWithEmployeesResponse]:
    departments = department_service.get_all_with_employees(db)
    return [_department_with_employees_response(d) for d in departments]


def create_department(body: DepartmentCreate, db: Session) -> DepartmentResponse:
    existing = department_service.get_by_name(db, body.name)
    if existing:
        raise HTTPException(status_code=409, detail="A department with this name already exists.")
    dept = department_service.create(db, body)
    return DepartmentResponse.model_validate(dept)


def delete_department(id: int, db: Session) -> None:
    department = department_service.get_by_id(db, id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    try:
        department_service.delete(db, department)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete department that has employees. Reassign or remove employees first.",
        )
    return None


def bulk_create_departments(db: Session, names: list[str]) -> BulkResult:
    """Insert all new department names in one transaction. Duplicates (in list or DB) are skipped."""
    created = failed = 0
    seen: set[str] = set()
    for name in names:
        n = (name or "").strip()
        if not n:
            failed += 1
            continue
        key = n.lower()
        if key in seen:
            failed += 1
            continue
        if department_service.get_by_name(db, n):
            failed += 1
            continue
        db.add(Department(name=n))
        seen.add(key)
        created += 1
    db.commit()
    return BulkResult(created=created, updated=0, failed=failed)
