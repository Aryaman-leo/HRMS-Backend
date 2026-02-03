"""Attendance service: DB operations for attendance."""
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Attendance, Department, Employee


def get_all_with_employee_name(
    db: Session,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    stmt = (
        select(Attendance, Employee.full_name, Department.name)
        .join(Employee, Attendance.employee_id == Employee.employee_id)
        .outerjoin(Department, Department.id == Employee.department_id)
    )
    if date_from:
        stmt = stmt.where(Attendance.date >= date_from)
    if date_to:
        stmt = stmt.where(Attendance.date <= date_to)
    stmt = stmt.order_by(Attendance.date.desc(), Attendance.id)
    rows = db.execute(stmt).all()
    return [
        {
            "id": a.id,
            "date": a.date,
            "employee_id": a.employee_id,
            "employee_name": employee_name,
            "department_name": department_name,
            "status": a.status,
        }
        for a, employee_name, department_name in rows
    ]


def get_attendance_summary(db: Session) -> list[dict]:
    """Per-employee present/absent day counts. Includes all employees (0s if no records)."""
    stmt = (
        select(Attendance.employee_id, Attendance.status, func.count(Attendance.id).label("cnt"))
        .group_by(Attendance.employee_id, Attendance.status)
    )
    rows = db.execute(stmt).all()
    summary: dict[str, dict] = defaultdict(lambda: {"present_days": 0, "absent_days": 0})
    for employee_id, status, count in rows:
        key = employee_id
        if (status or "").lower() == "present":
            summary[key]["present_days"] = count
        else:
            summary[key]["absent_days"] = count

    from app.services import employee_service

    employees = employee_service.get_all(db)
    return [
        {
            "employee_id": emp.employee_id,
            "employee_name": emp.full_name,
            "present_days": summary[emp.employee_id]["present_days"],
            "absent_days": summary[emp.employee_id]["absent_days"],
        }
        for emp in employees
    ]


def get_by_employee_date(db: Session, employee_id: str, date: str) -> Attendance | None:
    return db.execute(
        select(Attendance).where(
            Attendance.employee_id == employee_id,
            Attendance.date == date,
        )
    ).scalar_one_or_none()


def create(db: Session, employee_id: str, date: str, status: str) -> Attendance:
    rec = Attendance(employee_id=employee_id, date=date, status=status)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update_status(db: Session, rec: Attendance, status: str) -> Attendance:
    rec.status = status
    db.commit()
    db.refresh(rec)
    return rec


def create_or_update(db: Session, employee_id: str, date: str, status: str) -> tuple[Attendance, str]:
    existing = get_by_employee_date(db, employee_id, date)
    if existing:
        update_status(db, existing, status)
        return existing, "updated"
    rec = create(db, employee_id, date, status)
    return rec, "created"


def to_response(
    rec: Attendance,
    employee_name: str | None = None,
    department_name: str | None = None,
) -> dict:
    return {
        "id": rec.id,
        "date": rec.date,
        "employee_id": rec.employee_id,
        "employee_name": employee_name,
        "department_name": department_name,
        "status": rec.status,
    }
