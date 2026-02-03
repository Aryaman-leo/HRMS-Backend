"""Admin log service: record and list admin actions."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminLog


def create(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str | int | None = None,
    details: str | None = None,
) -> AdminLog:
    log = AdminLog(
        action=action.strip(),
        entity_type=entity_type.strip(),
        entity_id=str(entity_id) if entity_id is not None else None,
        details=(details or "").strip() or None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(
    db: Session,
    limit: int = 200,
    offset: int = 0,
    entity_type: str | None = None,
    action: str | None = None,
) -> list[AdminLog]:
    stmt = select(AdminLog).order_by(AdminLog.created_at.desc())
    if entity_type:
        stmt = stmt.where(AdminLog.entity_type == entity_type)
    if action:
        stmt = stmt.where(AdminLog.action == action)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())
