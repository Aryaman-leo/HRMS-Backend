"""Routes for /api/admin-logs. Read-only list of admin actions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import admin_log_controller
from app.database import get_db
from app.schemas import AdminLogResponse

router = APIRouter(prefix="/admin-logs", tags=["admin-logs"])


@router.get("", response_model=list[AdminLogResponse])
def list_admin_logs(
    limit: int = 200,
    offset: int = 0,
    entity_type: str | None = None,
    action: str | None = None,
    db: Session = Depends(get_db),
):
    """List admin action logs (newest first). Optional filters: entity_type, action."""
    return admin_log_controller.list_logs(db, limit=limit, offset=offset, entity_type=entity_type, action=action)
