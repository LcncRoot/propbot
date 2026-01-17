"""SQLite database connection management for PropBot."""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from ..config import config


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """
    Get a SQLite database connection.

    Args:
        db_path: Optional path to database file. Defaults to config.DATABASE_PATH.

    Returns:
        SQLite connection with row factory set for dict-like access.
    """
    path = db_path or config.DATABASE_PATH

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints

    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.

    Automatically commits on success, rolls back on exception.

    Usage:
        with get_db() as conn:
            conn.execute("INSERT INTO ...")
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path | None = None) -> None:
    """
    Initialize the database by creating all tables.

    Args:
        db_path: Optional path to database file. Defaults to config.DATABASE_PATH.
    """
    from .migrations import run_migrations

    conn = get_connection(db_path)
    try:
        run_migrations(conn)
        conn.commit()
    finally:
        conn.close()
