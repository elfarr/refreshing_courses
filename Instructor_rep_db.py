from __future__ import annotations
from typing import List, Optional
import psycopg2
import psycopg2.extras

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile


class InstructorRepDB:
    def __init__(self, *, host: str, port: int, dbname: str, user: str, password: str):
        self.conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        self.conn.autocommit = True  

    def close(self):
        self.conn.close()

    def get_by_id(self, instructor_id: int) -> Optional[Instructor]:
        sql = """
        SELECT instructor_id, last_name, first_name, patronymic, phone, experience_years
        FROM instructors
        WHERE instructor_id = %s
        """
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (instructor_id,))
            row = cur.fetchone()
            return Instructor(dict(row)) if row else None

    def get_k_n_short_list(self, k: int, n: int) -> List[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        offset = (k - 1) * n
        sql = """
        SELECT instructor_id, last_name, first_name, patronymic, phone, experience_years
        FROM instructors
        ORDER BY last_name, first_name, patronymic NULLS LAST, instructor_id
        LIMIT %s OFFSET %s
        """
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (n, offset))
            rows = cur.fetchall() or []
            return [PublicInstructorProfile(dict(r)) for r in rows]

    def add(self, item: Instructor) -> Instructor:
        if not isinstance(item.instructor_id, int) or item.instructor_id <= 0:
            raise ValueError("instructor_id обязателен и должен быть > 0")

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 1
                FROM instructors
                WHERE last_name = %s
                AND first_name = %s
                AND COALESCE(patronymic, '') = COALESCE(%s, '')
                AND experience_years = %s
                LIMIT 1
            """, (item.last_name, item.first_name, item.patronymic, item.experience_years))
            if cur.fetchone():
                raise ValueError("такой Instructor уже существует (равенство по ФИО+стаж)")

            cur.execute("SELECT 1 FROM instructors WHERE instructor_id = %s", (item.instructor_id,))
            if cur.fetchone():
                raise ValueError(f"instructor_id {item.instructor_id} уже существует")
            
            cur.execute("""
                INSERT INTO instructors (instructor_id, last_name, first_name, patronymic, phone, experience_years)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item.instructor_id, item.last_name, item.first_name, item.patronymic, item.phone, item.experience_years))

        return Instructor(
            item.instructor_id,
            item.last_name,
            item.first_name,
            item.patronymic,
            item.phone,
            item.experience_years,
        )

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        sql = """
        UPDATE instructors
        SET last_name=%s, first_name=%s, patronymic=%s, phone=%s, experience_years=%s
        WHERE instructor_id=%s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (
                new_item.last_name, new_item.first_name, new_item.patronymic,
                new_item.phone, new_item.experience_years, instructor_id
            ))
            return cur.rowcount > 0

    def delete_by_id(self, instructor_id: int) -> bool:
        sql = "DELETE FROM instructors WHERE instructor_id=%s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (instructor_id,))
            return cur.rowcount > 0

    def get_count(self) -> int:
        sql = "SELECT COUNT(*) FROM instructors"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return int(cur.fetchone()[0])
