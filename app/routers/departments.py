"""Routes for /api/departments. Delegates to controller."""
import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.controllers import department_controller
from app.database import get_db
from app.schemas import BulkResult, DepartmentBulkCreate, DepartmentCreate, DepartmentResponse, DepartmentWithEmployeesResponse

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentWithEmployeesResponse])
def list_departments(db: Session = Depends(get_db)):
    return department_controller.list_departments(db)


@router.post("", status_code=201, response_model=DepartmentResponse)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db)):
    return department_controller.create_department(body, db)


@router.post("/bulk", response_model=BulkResult)
def bulk_create_departments(body: DepartmentBulkCreate, db: Session = Depends(get_db)):
    """Bulk create departments from JSON: body.names = [\"Engineering\", \"HR\", ...]."""
    return department_controller.bulk_create_departments(db, body.names)


@router.post("/bulk/csv", response_model=BulkResult)
async def bulk_create_departments_csv(
    file: UploadFile = File(..., description="CSV with a 'name' column (or first column = department name)"),
    db: Session = Depends(get_db),
):
    """Bulk create departments from CSV. CSV must have header row with column 'name', or no header (first column = name)."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file.")
    try:
        raw = await file.read()
        text = raw.decode("utf-8-sig").strip()
    except Exception as e:
        raise HTTPException(400, f"Could not read file as UTF-8: {e}") from e
    if not text:
        raise HTTPException(400, "CSV file is empty.")
    reader = csv.reader(io.StringIO(text))
    rows = [r for r in reader if r]
    if not rows:
        raise HTTPException(400, "No rows in CSV.")
    # If first cell is "name", treat as header
    if rows[0][0].strip().lower() == "name":
        names = [(r[0] or "").strip() for r in rows[1:] if r and (r[0] or "").strip()]
    else:
        names = [(r[0] or "").strip() for r in rows if r and (r[0] or "").strip()]
    if not names:
        raise HTTPException(400, "No department names found in CSV.")
    return department_controller.bulk_create_departments(db, names)


@router.delete("/{id}", status_code=204)
def delete_department(id: int, db: Session = Depends(get_db)):
    return department_controller.delete_department(id, db)
