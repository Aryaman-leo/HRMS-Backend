"""Routes for /api/employees. Delegates to controller."""
import csv
import io
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.controllers import employee_controller
from app.database import get_db
from app.schemas import BulkResult, EmployeeBulkCreate, EmployeeCreate, EmployeeResponse
from app.services import department_service

router = APIRouter(prefix="/employees", tags=["employees"])


def _norm_key(s: str) -> str:
    return re.sub(r"\s+", "_", (s or "").strip().lower())


@router.get("", response_model=list[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return employee_controller.list_employees(db)


@router.post("", status_code=201, response_model=EmployeeResponse)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_controller.create_employee(body, db)


@router.delete("/{id_or_employee_id}", status_code=204)
def delete_employee(id_or_employee_id: str, db: Session = Depends(get_db)):
    return employee_controller.delete_employee(id_or_employee_id, db)


@router.post("/bulk", response_model=BulkResult)
def bulk_create_employees(body: EmployeeBulkCreate, db: Session = Depends(get_db)):
    """Bulk create employees from JSON: body.employees = [{ employeeId, fullName, email, departmentId }, ...]."""
    return employee_controller.bulk_create_employees(db, body.employees)


@router.post("/bulk/csv", response_model=BulkResult)
async def bulk_create_employees_csv(
    file: UploadFile = File(..., description="CSV: employee_id, full_name, email, department_id (or department_name)"),
    db: Session = Depends(get_db),
):
    """Bulk create employees from CSV. Columns: employee_id (or employeeId), full_name (or fullName), email, department_id (or departmentId) or department_name."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file.")
    try:
        raw = await file.read()
        text = raw.decode("utf-8-sig").strip()
    except Exception as e:
        raise HTTPException(400, f"Could not read file as UTF-8: {e}") from e
    if not text:
        raise HTTPException(400, "CSV file is empty.")
    reader = csv.DictReader(io.StringIO(text))
    # Normalize column names: strip, lowercase, spaces -> underscores
    if not reader.fieldnames:
        raise HTTPException(400, "CSV has no header row.")
    key_map = {_norm_key(f): f for f in reader.fieldnames}
    def get(row: dict, *candidates: str) -> str | None:
        for c in candidates:
            k = _norm_key(c)
            if k in key_map and row.get(key_map[k]):
                return (row.get(key_map[k]) or "").strip()
        return None
    employees: list[EmployeeCreate] = []
    dept_by_name: dict[str, int] = {}
    for row in reader:
        eid = get(row, "employee_id", "employeeId", "employee id")
        full_name = get(row, "full_name", "fullName", "full name")
        email = get(row, "email")
        dept_id_val = get(row, "department_id", "departmentId", "department id")
        dept_name_val = get(row, "department_name", "departmentName", "department name")
        if not eid or not full_name or not email:
            continue
        department_id: int | None = None
        if dept_id_val and dept_id_val.isdigit():
            department_id = int(dept_id_val)
        elif dept_name_val:
            if dept_name_val not in dept_by_name:
                d = department_service.get_by_name(db, dept_name_val)
                if d:
                    dept_by_name[dept_name_val] = d.id
            department_id = dept_by_name.get(dept_name_val)
        if department_id is None:
            continue
        try:
            employees.append(
                EmployeeCreate(employeeId=eid, fullName=full_name, email=email, departmentId=department_id)
            )
        except Exception:
            continue
    if not employees:
        raise HTTPException(400, "No valid employee rows (need employee_id, full_name, email, department_id or department_name).")
    return employee_controller.bulk_create_employees(db, employees)
