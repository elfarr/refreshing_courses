from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import threading
from typing import Any

import psycopg2
import psycopg2.extras


class PostgresDB:
    _instance: PostgresDB | None = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> PostgresDB:
        if cls._instance is None:
            # выполняется только один поток, второй ждёт
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, host: str, port: int, dbname: str, user: str, password: str) -> None:
        if getattr(self, "_inited", False):
            return
        self._conn: Any = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
        self._conn.autocommit = True
        self._inited: bool = True

    @contextmanager
    def cursor(self) -> Iterator[Any]:
        cur: Any = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> int:
        with self.cursor() as cur:
            cur.execute(sql, params or ())
            # rowcount гарантированно int
            return int(cur.rowcount)

    def fetchone(self, sql: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        with self.cursor() as cur:
            cur.execute(sql, params or ())
            row: Any = cur.fetchone()
            # cur.fetchone() может вернуть None либо dict-like
            return dict(row) if row else None

    def fetchall(self, sql: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(sql, params or ())
            rows: Any = cur.fetchall() or []
            return [dict(r) for r in rows]

    def close(self) -> None:
        if getattr(self, "_conn", None):
            self._conn.close()
            self._conn = None
            self._inited = False
