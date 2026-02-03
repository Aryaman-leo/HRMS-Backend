# HRMS Lite – Backend

FastAPI + SQLite backend for the HRMS Lite frontend.  
Provides REST APIs for managing employees, departments, and attendance.

---

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Uvicorn

---

## Project Structure

Separation of concerns with a clean layered architecture:

app/  
models/        → SQLAlchemy models (Department, Employee, Attendance)  
schemas/       → Pydantic request/response models  
services/      → Business logic and DB operations (no HTTP)  
controllers/   → HTTP layer: validation, status codes, calls services  
routers/       → Route definitions, delegate to controllers  
database.py    → DB engine and session  
main.py        → FastAPI app, CORS, lifespan, include routers  

Flow:  
Router → Controller → Service → Model

---

## Setup

### 1. Create virtual environment

Windows:  
python -m venv .venv  
.venv\Scripts\activate  

macOS / Linux:  
python -m venv .venv  
source .venv/bin/activate  

---

### 2. Install dependencies

pip install -r requirements.txt

---

### 3. (Optional) Environment config

Create a .env file if needed:

DATABASE_URL=sqlite:///./hrms.db

---

### 4. Seed the database

Seeds departments, sample employees, and attendance.

python seed.py

If you had an older schema, delete hrms.db first so tables are recreated.

---

### 5. Start the server

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

API base URL:  
http://localhost:8000

---

## Frontend Configuration

Set in frontend .env:

VITE_API_URL=http://localhost:8000

CORS is enabled for:  
http://localhost:5173  
http://127.0.0.1:5173  

---

## API Endpoints

Departments:  
GET /api/departments → List all departments  
POST /api/departments → Create department  
DELETE /api/departments/{id} → Delete department  

Employees:  
GET /api/employees → List all employees  
POST /api/employees → Create employee  
DELETE /api/employees/{id} → Delete employee  

Attendance:  
GET /api/attendance → List all attendance  
POST /api/attendance → Create/update one  
POST /api/attendance/bulk → Bulk create/update  

---

## Error Handling

All errors return:

{ "detail": "Error message" }

---

## Summary

Production-style HRMS backend with clean architecture, proper validations, real-world workflows, frontend-ready APIs, and structured error handling.
