"""FastAPI app: CORS, lifespan (DB init), routers under /api."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.db_migrations import ensure_employees_department_id, ensure_employees_email_unique
from app.models import Attendance, Department, Employee  # noqa: F401 - register tables with Base
from app.routers import attendance, departments, employees


@asynccontextmanager
async def lifespan(app: FastAPI):
    # If an older hrms.db exists, migrate it before ORM queries run.
    ensure_employees_department_id(engine)
    ensure_employees_email_unique(engine)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="HRMS Lite API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hrmsinterview.netlify.app",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
