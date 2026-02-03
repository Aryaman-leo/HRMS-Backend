"""Admin log controller: list logs."""
from sqlalchemy.orm import Session

from app.schemas import AdminLogResponse
from app.services import admin_log_service


def list_logs(
    db: Session,
    limit: int = 200,
    offset: int = 0,
    entity_type: str | None = None,
    action: str | None = None,
) -> list[AdminLogResponse]:
    logs = admin_log_service.list_logs(db, limit=limit, offset=offset, entity_type=entity_type, action=action)
    return [AdminLogResponse.model_validate(log) for log in logs]
