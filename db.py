"""Low-level MySQL connection and query helpers."""

from __future__ import annotations

from typing import Any

from connect import connect_database


class Database:
    """Creates short-lived connections and provides basic query operations."""

    def connection(self):
        connection = connect_database()
        if connection is None:
            raise RuntimeError(
                "Could not connect to MySQL. Check that the server is running, "
                "the database has been imported, and MYSQL_* settings are correct."
            )
        return connection

    def rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        connection = self.connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            connection.close()

    def row(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        result = self.rows(sql, params)
        return result[0] if result else None

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        connection = self.connection()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            connection.commit()
            return cursor.lastrowid
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()