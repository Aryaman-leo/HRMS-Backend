"""Employee service: DB operations for employees."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Employee
from app.schemas import EmployeeCreate


def get_all(db: Session) -> list[Employee]:
    return list(
        db.execute(
            select(Employee).options(joinedload(Employee.department)).order_by(Employee.id)
        ).unique().scalars().all()
    )


def get_by_id(db: Session, id: int) -> Employee | None:
    return db.get(Employee, id)


def get_by_employee_id(db: Session, employee_id: str) -> Employee | None:
    return (
        db.execute(
            select(Employee).options(joinedload(Employee.department)).where(Employee.employee_id == employee_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def get_by_email(db: Session, email: str) -> Employee | None:
    normalized = email.strip().lower()
    return (
        db.execute(
            select(Employee).options(joinedload(Employee.department)).where(Employee.email == normalized)
        )
        .unique()
        .scalar_one_or_none()
    )


def create(db: Session, data: EmployeeCreate) -> Employee:
    emp = Employee(
        employee_id=data.employee_id.strip(),
        full_name=data.full_name.strip(),
        email=data.email.strip().lower(),
        department_id=data.department_id,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def delete(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()
