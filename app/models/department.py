"""Department model."""
from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False, index=True)

    employees = relationship("Employee", back_populates="department")
