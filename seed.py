"""Seed DB with departments, Indian-name employees, and sample attendance. Idempotent: skips if data exists."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.db_migrations import ensure_employees_department_id
from app.models import Attendance, Department, Employee

SEED_DEPARTMENTS = ["Engineering", "HR", "Sales", "Finance"]

SEED_EMPLOYEES = [
    {"employee_id": "EMP001", "full_name": "Priya Sharma", "email": "priya.sharma@example.com", "department_name": "Engineering"},
    {"employee_id": "EMP002", "full_name": "Raj Kumar", "email": "raj.kumar@example.com", "department_name": "Sales"},
    {"employee_id": "EMP003", "full_name": "Ananya Singh", "email": "ananya.singh@example.com", "department_name": "HR"},
    {"employee_id": "EMP004", "full_name": "Vikram Patel", "email": "vikram.patel@example.com", "department_name": "Engineering"},
    {"employee_id": "EMP005", "full_name": "Meera Reddy", "email": "meera.reddy@example.com", "department_name": "Finance"},
]

SAMPLE_ATTENDANCE = [
    ("EMP001", "2025-02-01", "Present"),
    ("EMP002", "2025-02-01", "Present"),
    ("EMP003", "2025-02-01", "Absent"),
    ("EMP004", "2025-02-01", "Present"),
    ("EMP005", "2025-02-01", "Present"),
    ("EMP001", "2025-02-02", "Present"),
    ("EMP002", "2025-02-02", "Absent"),
    ("EMP003", "2025-02-02", "Present"),
    ("EMP004", "2025-02-02", "Present"),
    ("EMP005", "2025-02-02", "Present"),
]


def seed():
    # Handle older schema where employees.department_id didn't exist yet.
    ensure_employees_department_id(engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_emp = db.execute(select(Employee).limit(1)).scalar_one_or_none()
        if existing_emp:
            print("Employees already exist; skipping seed.")
            return

        existing_dept = db.execute(select(Department).limit(1)).scalar_one_or_none()
        if not existing_dept:
            for name in SEED_DEPARTMENTS:
                db.add(Department(name=name))
            db.commit()
            print("Added", len(SEED_DEPARTMENTS), "departments.")

        name_to_id = {d.name: d.id for d in db.execute(select(Department)).scalars().all()}
        for data in SEED_EMPLOYEES:
            dept_name = data.pop("department_name")
            dept_id = name_to_id.get(dept_name)
            if dept_id is None:
                dept = db.execute(select(Department).where(Department.name == dept_name)).scalar_one_or_none()
                if dept:
                    dept_id = dept.id
                else:
                    dept = Department(name=dept_name)
                    db.add(dept)
                    db.flush()
                    dept_id = dept.id
            db.add(Employee(**data, department_id=dept_id))
        db.commit()
        print("Added", len(SEED_EMPLOYEES), "employees.")

        for employee_id, date, status in SAMPLE_ATTENDANCE:
            db.add(Attendance(employee_id=employee_id, date=date, status=status))
        db.commit()
        print("Added", len(SAMPLE_ATTENDANCE), "attendance records.")
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
