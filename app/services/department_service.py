"""Department service: DB operations for departments."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Department
from app.schemas import DepartmentCreate


def get_all(db: Session) -> list[Department]:
    return list(db.execute(select(Department).order_by(Department.name)).scalars().all())


def get_all_with_employees(db: Session) -> list[Department]:
    """Fetch all departments with their employees in a single query."""
    return list(
        db.execute(
            select(Department)
            .options(joinedload(Department.employees))
            .order_by(Department.name)
        )
        .unique()
        .scalars()
        .all()
    )


def get_by_id(db: Session, id: int) -> Department | None:
    return db.get(Department, id)


def get_by_name(db: Session, name: str) -> Department | None:
    return db.execute(select(Department).where(Department.name == name.strip())).scalar_one_or_none()


def create(db: Session, data: DepartmentCreate) -> Department:
    dept = Department(name=data.name.strip())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def delete(db: Session, department: Department) -> None:
    db.delete(department)
    db.commit()
