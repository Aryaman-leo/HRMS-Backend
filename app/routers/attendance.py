"""Routes for /api/attendance. Delegates to controller."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import attendance_controller
from app.database import get_db
from app.schemas import (
    AttendanceBulkCreate,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryItem,
    BulkResult,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("", response_model=list[AttendanceResponse])
def list_attendance(
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
):
    """List attendance records. Optionally filter by date range (YYYY-MM-DD)."""
    return attendance_controller.list_attendance(db, date_from=date_from, date_to=date_to)


@router.get("/summary", response_model=list[AttendanceSummaryItem])
def list_attendance_summary(db: Session = Depends(get_db)):
    """Per-employee total present and absent days."""
    return attendance_controller.list_attendance_summary(db)


@router.post("", status_code=201, response_model=AttendanceResponse)
def create_attendance(body: AttendanceCreate, db: Session = Depends(get_db)):
    return attendance_controller.create_attendance(body, db)


@router.post("/bulk", response_model=BulkResult)
def bulk_attendance(body: AttendanceBulkCreate, db: Session = Depends(get_db)):
    return attendance_controller.bulk_attendance(body, db)
