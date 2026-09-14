import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.models import HistoryEntry


class HistoryService:
    """Persist local chat and incident records without external services."""

    def __init__(self, database_path: str, max_entries: int = 1_000) -> None:
        if max_entries < 1:
            raise ValueError("History retention must be at least one entry")
        self.database_path = database_path
        self.max_entries = max_entries
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    request TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def record(self, category: str, request: str, response: str) -> HistoryEntry:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO history (category, request, response, created_at) VALUES (?, ?, ?, ?)",
                (category, request, response, created_at),
            )
            connection.execute(
                """
                DELETE FROM history
                WHERE id NOT IN (
                    SELECT id FROM history ORDER BY id DESC LIMIT ?
                )
                """,
                (self.max_entries,),
            )
        return HistoryEntry(
            id=cursor.lastrowid,
            category=category,
            request=request,
            response=response,
            created_at=created_at,
        )

    def list_entries(self, limit: int) -> list[HistoryEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, category, request, response, created_at
                FROM history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [HistoryEntry(**dict(row)) for row in rows]

    def clear(self) -> int:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM history")
        return cursor.rowcount

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
