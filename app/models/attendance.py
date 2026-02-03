"""Attendance model."""
from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        Text,
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Text, nullable=False)
    status = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("employee_id", "date", name="uq_employee_date"),)

    employee = relationship("Employee", back_populates="attendance")
