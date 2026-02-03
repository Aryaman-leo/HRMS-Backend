"""Lightweight DB migrations for SQLite.

This project intentionally avoids Alembic for simplicity, but we still need to
handle schema drift when an older `hrms.db` is present.
"""

from __future__ import annotations

from sqlalchemy import Engine, text


def _is_sqlite(engine: Engine) -> bool:
    try:
        return engine.dialect.name == "sqlite"
    except Exception:
        return False


def ensure_employees_department_id(engine: Engine) -> None:
    """Ensure `employees.department_id` exists and is backfilled.

    Older DB versions used `employees.department` (TEXT). Newer code expects a
    `department_id` FK to `departments.id`. This migrates old DBs in-place:
    - add `department_id` column if missing
    - create missing departments referenced by `employees.department`
    - backfill `department_id` from the department name
    - create an index on `department_id`
    - drop legacy `department` column so INSERT uses only department_id
    """

    if not _is_sqlite(engine):
        return

    with engine.begin() as conn:
        # Get columns from SQLite schema
        cols = conn.execute(text("PRAGMA table_info(employees)")).fetchall()
        if not cols:
            # employees table doesn't exist yet; create_all() will handle it
            return

        col_names = {row[1] for row in cols}  # pragma: table_info -> (cid, name, type, notnull, dflt, pk)
        has_department_id = "department_id" in col_names
        has_old_department = "department" in col_names

        if not has_department_id:
            # Can't add NOT NULL via ALTER TABLE on SQLite unless default is provided.
            conn.execute(text("ALTER TABLE employees ADD COLUMN department_id INTEGER"))
            has_department_id = True

        if has_department_id and has_old_department:
            # Ensure departments exist for all distinct employee.department values
            dept_names = [
                r[0]
                for r in conn.execute(
                    text(
                        """
                        SELECT DISTINCT TRIM(department) AS name
                        FROM employees
                        WHERE department IS NOT NULL AND TRIM(department) <> ''
                        """
                    )
                ).fetchall()
            ]

            for name in dept_names:
                dept_id = conn.execute(
                    text("SELECT id FROM departments WHERE name = :name"),
                    {"name": name},
                ).scalar_one_or_none()
                if dept_id is None:
                    conn.execute(text("INSERT INTO departments(name) VALUES (:name)"), {"name": name})
                    dept_id = conn.execute(
                        text("SELECT id FROM departments WHERE name = :name"),
                        {"name": name},
                    ).scalar_one()

                conn.execute(
                    text(
                        """
                        UPDATE employees
                        SET department_id = :dept_id
                        WHERE (department_id IS NULL OR department_id = '')
                          AND TRIM(department) = :name
                        """
                    ),
                    {"dept_id": dept_id, "name": name},
                )

        # Helpful index for joins/filters; safe to run repeatedly.
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_employees_department_id ON employees(department_id)")
        )

        # Drop legacy TEXT column so INSERT only uses department_id (avoids NOT NULL on department).
        # SQLite 3.35.0+ supports DROP COLUMN.
        if has_old_department:
            try:
                conn.execute(text("ALTER TABLE employees DROP COLUMN department"))
            except Exception:
                # Old SQLite or other DB: ignore; app may still work if column is nullable
                pass


def ensure_employees_email_unique(engine: Engine) -> None:
    """Ensure employees.email has a unique index so the same email cannot be added twice.

    Only creates the index when there are no duplicate emails (e.g. existing DBs
    that already have duplicates keep app-level validation only).
    """
    if not _is_sqlite(engine):
        return

    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(employees)")).fetchall()
        if not cols:
            return
        col_names = {row[1] for row in cols}
        if "email" not in col_names:
            return

        # Skip if duplicates exist; app-level check will still prevent new duplicates.
        dup = conn.execute(
            text(
                """
                SELECT 1 FROM (
                    SELECT LOWER(TRIM(email)) AS e, COUNT(*) AS c FROM employees GROUP BY e HAVING c > 1
                ) LIMIT 1
                """
            )
        ).scalar_one_or_none()
        if dup:
            return

        try:
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_employees_email ON employees(email)"))
        except Exception:
            pass
