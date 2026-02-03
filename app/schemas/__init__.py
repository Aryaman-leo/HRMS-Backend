"""Pydantic request/response models for API."""
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# --- Department ---

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1)


class DepartmentBulkCreate(BaseModel):
    """Bulk create departments by name. Duplicates (in body or DB) are skipped (counted as failed)."""
    names: list[str] = Field(..., min_length=1)


class DepartmentResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class EmployeeSummary(BaseModel):
    """Minimal employee fields for nested display (e.g. under a department)."""
    id: int
    employee_id: str = Field(..., alias="employeeId")
    full_name: str = Field(..., alias="fullName")
    email: str

    model_config = {"from_attributes": True, "populate_by_name": True}


class DepartmentWithEmployeesResponse(BaseModel):
    id: int
    name: str
    employees: list[EmployeeSummary] = Field(default_factory=list, alias="employees")

    model_config = {"from_attributes": True, "populate_by_name": True}


# --- Employee ---

class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, alias="employeeId")
    full_name: str = Field(..., min_length=1, alias="fullName")
    email: EmailStr
    department_id: int = Field(..., alias="departmentId")

    model_config = {"populate_by_name": True}


class EmployeeResponse(BaseModel):
    id: int
    employee_id: str = Field(..., alias="employeeId")
    full_name: str = Field(..., alias="fullName")
    email: str
    department_id: int = Field(..., alias="departmentId")
    department: str = Field(..., alias="departmentName")

    model_config = {"from_attributes": True, "populate_by_name": True}


class EmployeeBulkCreate(BaseModel):
    """Bulk create employees. Duplicates (employee_id/email) in body or DB are skipped (counted as failed)."""
    employees: list[EmployeeCreate] = Field(..., min_length=1)


# --- Attendance ---

class AttendanceCreate(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    status: Literal["Present", "Absent"]

    model_config = {"populate_by_name": True}


class AttendanceRecordItem(BaseModel):
    employee_id: str = Field(..., alias="employeeId")
    status: Literal["Present", "Absent"]

    model_config = {"populate_by_name": True}


class AttendanceBulkCreate(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    records: list[AttendanceRecordItem] = Field(..., min_length=1)


class AttendanceResponse(BaseModel):
    id: int
    date: str
    employee_id: str = Field(..., alias="employeeId")
    employee_name: str | None = Field(None, alias="employeeName")
    status: str

    model_config = {"from_attributes": True, "populate_by_name": True}


class BulkResult(BaseModel):
    created: int = 0
    updated: int = 0
    failed: int = 0
