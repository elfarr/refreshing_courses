from __future__ import annotations

from collections.abc import Callable
from queue import Queue
from typing import Any

from file_repo_decorator import FileFilterSortDecorator
from file_spec import FileQuerySpec
from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile
from repo_decorators import DbFilterSortDecorator
from spec import QuerySpec
from webapp.observable_repo import ObservableInstructorRepo, RepoEvent
from webapp.serializers import as_public_dict


# оборачивает Наблюдателя для инструктора, чтобы мы могли уведомлять подписчиков на события
class InstructorController:
    def __init__(self, repo: ObservableInstructorRepo):
        self._repo = repo

    def count(self, filters: dict[str, Any] | None = None) -> int:
        spec = self._build_spec(filters)
        return self._repo.get_count(spec)

    # возвращаются публичные профили
    def list_profiles(
        self, k: int = 1, n: int | None = None, filters: dict[str, Any] | None = None
    ) -> list[PublicInstructorProfile]:
        limit = n if n is not None else max(self.count(filters), 1)
        spec = self._build_spec(filters)
        return self._repo.get_k_n_short_list(k, limit, spec)

    # возвращаются словари в нужном нам формате для ui
    def list_profiles_payload(
        self, k: int = 1, n: int | None = None, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return [as_public_dict(p) or {} for p in self.list_profiles(k, n, filters)]

    def get_instructor(self, instructor_id: int) -> Instructor | None:
        return self._repo.get_by_id(instructor_id)

    # находим информацию по конкретному инструктору
    def get_instructor_payload(self, instructor_id: int) -> dict[str, Any] | None:
        entity = self.get_instructor(instructor_id)
        return as_public_dict(entity)

    # создаем объект инструктора из данных что у нас есть
    def create_instructor(self, data: dict[str, Any]) -> dict[str, Any]:
        instr = self._build_instructor(data, fallback_id=int(data.get("instructor_id") or 1))
        created = self._repo.add(instr)
        return as_public_dict(created) or {}

    # заменяем данные по инструктору по id
    def update_instructor(self, instructor_id: int, data: dict[str, Any]) -> dict[str, Any]:
        instr = self._build_instructor(data, fallback_id=instructor_id)
        instr.instructor_id = instructor_id
        if not self._repo.replace_by_id(instructor_id, instr):
            raise ValueError(f"Инструктор #{instructor_id} не найден")
        updated = self._repo.get_by_id(instructor_id)
        return as_public_dict(updated) or {}

    def delete_instructor(self, instructor_id: int) -> bool:
        return self._repo.delete_by_id(instructor_id)

    # оформление "подписки" на обновление конкретного инструктора
    def subscribe_to_instructor(
        self, instructor_id: int | None = None
    ) -> tuple[Queue[RepoEvent], Callable[[], None]]:
        return self._repo.subscribe(instructor_id)

    def _build_instructor(self, data: dict[str, Any], fallback_id: int) -> Instructor:
        try:
            instructor_id = int(data.get("instructor_id", fallback_id) or fallback_id)
        except (TypeError, ValueError):
            instructor_id = fallback_id

        try:
            last_name = data["last_name"]
            first_name = data["first_name"]
            phone = data["phone"]
            experience_years = data["experience_years"]
        except KeyError as exc:
            raise ValueError() from exc

        patronymic = data.get("patronymic")
        return Instructor(
            instructor_id,
            str(last_name),
            str(first_name),
            None if patronymic in ("", None) else str(patronymic),
            str(phone),
            int(experience_years),
        )

    def _build_spec(self, filters: dict[str, Any] | None) -> FileQuerySpec | QuerySpec | None:
        if not filters:
            return None
        base = getattr(self._repo, "_base", None)
        last_name = filters.get("last_name") or ""
        first_name = filters.get("first_name") or ""
        min_exp = filters.get("min_exp")
        max_exp = filters.get("max_exp")
        order_by = filters.get("order_by") or ""

        if isinstance(base, FileFilterSortDecorator):

            def predicate(ins: Instructor) -> bool:
                ok = True
                if last_name:
                    ok = ok and last_name.lower() in (ins.last_name or "").lower()
                if first_name:
                    ok = ok and first_name.lower() in (ins.first_name or "").lower()
                if min_exp is not None:
                    ok = ok and ins.experience_years >= min_exp
                if max_exp is not None:
                    ok = ok and ins.experience_years <= max_exp
                return ok

            key: Callable[[Instructor], Any] | None = None
            reverse = False
            if order_by:
                parts = order_by.split()
                field = parts[0]
                reverse = len(parts) > 1 and parts[1].lower() == "desc"

                def _key(ins: Instructor) -> Any:
                    return getattr(ins, field, None)

                key = _key
            return FileQuerySpec(predicate=predicate, key=key, reverse=reverse)

        if isinstance(base, DbFilterSortDecorator):
            clauses = []
            params: list[Any] = []
            if last_name:
                clauses.append("lower(last_name) LIKE %s")
                params.append(f"%{last_name.lower()}%")
            if first_name:
                clauses.append("lower(first_name) LIKE %s")
                params.append(f"%{first_name.lower()}%")
            if min_exp is not None:
                clauses.append("experience_years >= %s")
                params.append(min_exp)
            if max_exp is not None:
                clauses.append("experience_years <= %s")
                params.append(max_exp)
            where = " AND ".join(clauses)
            return QuerySpec(where=where, params=tuple(params), order_by=order_by or "")

        return None


__all__ = ["InstructorController"]
