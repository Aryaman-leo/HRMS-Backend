"""One-time seed endpoint to populate DB with sample data. Enable with ENABLE_SEED=1."""
import os

from fastapi import APIRouter, HTTPException

from app.seed_runner import run_seed

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("")
def seed_db():
    """Run seed script (departments, employees, sample attendance). Idempotent; skips if data exists."""
    if os.getenv("ENABLE_SEED", "").lower() not in ("1", "true", "yes"):
        raise HTTPException(403, "Seed disabled. Set ENABLE_SEED=1 in environment to allow.")
    run_seed()
    return {"message": "Seed completed."}
