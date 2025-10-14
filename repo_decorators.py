from __future__ import annotations
from typing import List
from spec import QuerySpec
from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile

class DbFilterSortDecorator:
    # белый список разрешённых полей сортировки 
    _ALLOWED_ORDER_FIELDS = {
        "last_name": "last_name",
        "first_name": "first_name",
        "patronymic": "patronymic",
        "instructor_id": "instructor_id",
        "experience_years": "experience_years",
        "phone": "phone",
    }
    _ORDER_DEFAULT = "ORDER BY last_name, first_name, patronymic NULLS LAST, instructor_id"

    def __init__(self, db_repo):
        # то что мы оборачиваем в декоратор 
        self._repo = db_repo          
        self._db = db_repo._adaptee.db if hasattr(db_repo, "_adaptee") else db_repo.db

    # просто вызываем оригинальные методы
    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._repo.get_by_id(instructor_id)

    def add(self, item: Instructor) -> Instructor | None:
        return self._repo.add(item)

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        return self._repo.replace_by_id(instructor_id, new_item)

    def delete_by_id(self, instructor_id: int) -> bool:
        return self._repo.delete_by_id(instructor_id)

    def get_k_n_short_list(self, k: int, n: int, spec: QuerySpec | None = None) -> List[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        spec = spec or QuerySpec()
        offset = (k - 1) * n

        base = """
        SELECT instructor_id, last_name, first_name, patronymic, phone, experience_years
        FROM instructors
        """
        # к скл запросу добавляем фильтры и сортировки
        where_sql = f"WHERE {spec.where}\n" if spec.where else ""
        order_sql = self._build_order_sql(spec.order_by)

        sql = f"{base}{where_sql}{order_sql}\nLIMIT %s OFFSET %s"
        params = tuple(spec.params) + (n, offset)
        rows = self._db.fetchall(sql, params)
        return [PublicInstructorProfile(r) for r in rows]

    def get_count(self, spec: QuerySpec | None = None) -> int:
        spec = spec or QuerySpec()
        sql = "SELECT COUNT(*) AS c FROM instructors "
        if spec.where:
            sql += f"WHERE {spec.where}"
        row = self._db.fetchone(sql, tuple(spec.params))
        return int(row["c"]) if row else 0

    # сборка ORDER BY по белому списку
    def _build_order_sql(self, order_by: str | None) -> str:
        if not order_by or not order_by.strip():
            return self._ORDER_DEFAULT

        parts = []
        for chunk in order_by.split(","):
            token = chunk.strip()
            if not token:
                continue
            pieces = token.split()
            field = pieces[0]
            if field not in self._ALLOWED_ORDER_FIELDS:
                return self._ORDER_DEFAULT
            sql_field = self._ALLOWED_ORDER_FIELDS[field]

            direction = ""
            if len(pieces) >= 2:
                dir_up = pieces[1].upper()
                if dir_up not in ("ASC", "DESC"):
                    return self._ORDER_DEFAULT
                direction = f" {dir_up}"
            parts.append(f"{sql_field}{direction}")

        if not parts:
            return self._ORDER_DEFAULT
        return "ORDER BY " + ", ".join(parts)
