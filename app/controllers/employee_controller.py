"""Employee controller: HTTP handling for employee endpoints."""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import BulkResult, EmployeeCreate, EmployeeResponse
from app.services import employee_service, department_service


def _employee_response(emp: Employee) -> EmployeeResponse:
    dept_name = emp.department.name if emp.department else ""
    return EmployeeResponse(
        id=emp.id,
        employee_id=emp.employee_id,
        full_name=emp.full_name,
        email=emp.email,
        department_id=emp.department_id,
        department=dept_name,
    )


def list_employees(db: Session) -> list[EmployeeResponse]:
    employees = employee_service.get_all(db)
    return [_employee_response(e) for e in employees]


def create_employee(body: EmployeeCreate, db: Session) -> EmployeeResponse:
    existing = employee_service.get_by_employee_id(db, body.employee_id.strip())
    if existing:
        raise HTTPException(status_code=409, detail="An employee with this employee ID already exists.")
    existing_email = employee_service.get_by_email(db, body.email)
    if existing_email:
        raise HTTPException(status_code=409, detail="An employee with this email already exists.")
    dept = department_service.get_by_id(db, body.department_id)
    if not dept:
        raise HTTPException(status_code=400, detail="Department not found.")
    emp = employee_service.create(db, body)
    return _employee_response(emp)


def delete_employee(id_or_employee_id: str, db: Session) -> None:
    employee: Employee | None = None
    if id_or_employee_id.isdigit():
        employee = employee_service.get_by_id(db, int(id_or_employee_id))
    if not employee:
        employee = employee_service.get_by_employee_id(db, id_or_employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    employee_service.delete(db, employee)
    return None


def bulk_create_employees(db: Session, employees: list[EmployeeCreate]) -> BulkResult:
    """Insert all new employees in one transaction. Duplicates (employee_id/email in list or DB) are skipped."""
    created = failed = 0
    seen_ids: set[str] = set()
    seen_emails: set[str] = set()
    for item in employees:
        eid = (item.employee_id or "").strip()
        email = (item.email or "").strip().lower()
        if not eid or not email:
            failed += 1
            continue
        if eid in seen_ids or email in seen_emails:
            failed += 1
            continue
        if employee_service.get_by_employee_id(db, eid) or employee_service.get_by_email(db, email):
            failed += 1
            continue
        dept = department_service.get_by_id(db, item.department_id)
        if not dept:
            failed += 1
            continue
        db.add(
            Employee(
                employee_id=eid,
                full_name=(item.full_name or "").strip(),
                email=email,
                department_id=item.department_id,
            )
        )
        seen_ids.add(eid)
        seen_emails.add(email)
        created += 1
    db.commit()
    return BulkResult(created=created, updated=0, failed=failed)
