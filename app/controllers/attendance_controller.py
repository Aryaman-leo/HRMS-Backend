"""Attendance controller: HTTP handling for attendance endpoints."""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import (
    AttendanceBulkCreate,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryItem,
    BulkResult,
)
from app.services import admin_log_service, attendance_service, employee_service


def list_attendance(
    db: Session,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[AttendanceResponse]:
    return attendance_service.get_all_with_employee_name(db, date_from=date_from, date_to=date_to)


def list_attendance_summary(db: Session) -> list[AttendanceSummaryItem]:
    rows = attendance_service.get_attendance_summary(db)
    return [AttendanceSummaryItem(**r) for r in rows]


def create_attendance(body: AttendanceCreate, db: Session) -> AttendanceResponse:
    emp = employee_service.get_by_employee_id(db, body.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")
    existing = attendance_service.get_by_employee_date(db, body.employee_id, body.date)
    dept_name = emp.department.name if getattr(emp, "department", None) else None
    if existing:
        attendance_service.update_status(db, existing, body.status)
        admin_log_service.create(
            db, "update", "attendance", body.employee_id,
            f"Updated attendance: {emp.full_name} on {body.date} → {body.status}",
        )
        return attendance_service.to_response(existing, emp.full_name, dept_name)
    rec = attendance_service.create(db, body.employee_id, body.date, body.status)
    admin_log_service.create(
        db, "create", "attendance", body.employee_id,
        f"Marked attendance: {emp.full_name} on {body.date} → {body.status}",
    )
    return attendance_service.to_response(rec, emp.full_name, dept_name)


def bulk_attendance(body: AttendanceBulkCreate, db: Session) -> BulkResult:
    created = updated = failed = 0
    for item in body.records:
        emp = employee_service.get_by_employee_id(db, item.employee_id)
        if not emp:
            failed += 1
            continue
        _, action = attendance_service.create_or_update(db, item.employee_id, body.date, item.status)
        if action == "created":
            created += 1
        else:
            updated += 1
    if created or updated:
        admin_log_service.create(
            db, "bulk_create", "attendance", None,
            f"Bulk attendance for {body.date}: {created} created, {updated} updated",
        )
    return {"created": created, "updated": updated, "failed": failed}
