"""Attendance service: DB operations for attendance."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Attendance, Department, Employee


def get_all_with_employee_name(db: Session) -> list[dict]:
    rows = (
        db.execute(
            select(Attendance, Employee.full_name, Department.name)
            .join(Employee, Attendance.employee_id == Employee.employee_id)
            .outerjoin(Department, Department.id == Employee.department_id)
            .order_by(Attendance.date.desc(), Attendance.id)
        )
        .all()
    )
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
