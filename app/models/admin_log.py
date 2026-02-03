"""Admin log model: records every admin action on the platform."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Text

from app.database import Base


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(Text, nullable=False, index=True)  # create, update, delete, bulk_create, etc.
    entity_type = Column(Text, nullable=False, index=True)  # employee, department, attendance
    entity_id = Column(Text, nullable=True)  # id or identifier of the entity
    details = Column(Text, nullable=True)  # human-readable description
