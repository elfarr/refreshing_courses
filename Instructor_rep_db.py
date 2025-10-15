from __future__ import annotations

from db_singleton import PostgresDB
from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile


class InstructorRepDB:
    def __init__(self, db: PostgresDB) -> None:
        self.db = db

    def close(self) -> None:
        pass

    def get_by_id(self, instructor_id: int) -> Instructor | None:
        sql = """
        SELECT instructor_id, last_name, first_name, patronymic, phone, experience_years
        FROM instructors
        WHERE instructor_id = %s
        """
        row = self.db.fetchone(sql, (instructor_id,))
        return Instructor(row) if row else None

    def get_k_n_short_list(self, k: int, n: int) -> list[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        offset = (k - 1) * n
        sql = """
        SELECT instructor_id, last_name, first_name, patronymic, phone, experience_years
        FROM instructors
        ORDER BY last_name, first_name, patronymic NULLS LAST, instructor_id
        LIMIT %s OFFSET %s
        """
        rows = self.db.fetchall(sql, (n, offset))
        return [PublicInstructorProfile(r) for r in rows]

    def add(self, item: Instructor) -> Instructor:
        if not isinstance(item.instructor_id, int) or item.instructor_id <= 0:
            raise ValueError("instructor_id обязателен и должен быть > 0")

        dup_row = self.db.fetchone(
            """
            SELECT 1
            FROM instructors
            WHERE last_name=%s AND first_name=%s
              AND COALESCE(patronymic,'') = COALESCE(%s,'')
              AND experience_years=%s
            LIMIT 1
        """,
            (item.last_name, item.first_name, item.patronymic, item.experience_years),
        )
        if dup_row:
            raise ValueError("такой Instructor уже существует (равенство по ФИО+стаж)")

        id_row = self.db.fetchone(
            "SELECT 1 FROM instructors WHERE instructor_id=%s", (item.instructor_id,)
        )
        if id_row:
            raise ValueError(f"instructor_id {item.instructor_id} уже существует")

        self.db.execute(
            """
            INSERT INTO instructors (instructor_id, last_name, first_name, patronymic, phone, experience_years)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (
                item.instructor_id,
                item.last_name,
                item.first_name,
                item.patronymic,
                item.phone,
                item.experience_years,
            ),
        )

        return Instructor(
            item.instructor_id,
            item.last_name,
            item.first_name,
            item.patronymic,
            item.phone,
            item.experience_years,
        )

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        count = self.db.execute(
            """
            UPDATE instructors
            SET last_name=%s, first_name=%s, patronymic=%s, phone=%s, experience_years=%s
            WHERE instructor_id=%s
        """,
            (
                new_item.last_name,
                new_item.first_name,
                new_item.patronymic,
                new_item.phone,
                new_item.experience_years,
                instructor_id,
            ),
        )
        return count > 0

    def delete_by_id(self, instructor_id: int) -> bool:
        count = self.db.execute("DELETE FROM instructors WHERE instructor_id=%s", (instructor_id,))
        return count > 0

    def get_count(self) -> int:
        row = self.db.fetchone("SELECT COUNT(*) AS c FROM instructors")
        return int(row["c"]) if row else 0
