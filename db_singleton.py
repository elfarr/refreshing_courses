from __future__ import annotations
import threading
from contextlib import contextmanager
import psycopg2
import psycopg2.extras


class PostgresDB:
    # храним единственный инстант
    _instance = None
    # чтобы не было ситуации что 2 потока создают по инстансу
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
             # выполняется только один поток, второй ждет
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *, host: str, port: int, dbname: str, user: str, password: str):
        if getattr(self, "_inited", False):
            return
        self._conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        # все изменения сразу применяются
        self._conn.autocommit = True
        # пометка что инициализирован 
        self._inited = True

    # оборачиваем добавляя методы энтер и екзит (энтер - подключаемся, выходим из with - закрываем соединение)
    @contextmanager
    def cursor(self):
        # оборачивает все что получает в реальные словари
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()

    def execute(self, sql: str, params: tuple | None = None) -> int:
        with self.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount

    def fetchone(self, sql: str, params: tuple | None = None) -> dict | None:
        with self.cursor() as cur:
            # замена none на ()
            cur.execute(sql, params or ())
            # вывод только первой строки
            row = cur.fetchone()
            return dict(row) if row else None

    def fetchall(self, sql: str, params: tuple | None = None) -> list[dict]:
        with self.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall() or []
            return [dict(r) for r in rows]

    def close(self):
        if getattr(self, "_conn", None):
            self._conn.close()
            self._conn = None
            self._inited = False
