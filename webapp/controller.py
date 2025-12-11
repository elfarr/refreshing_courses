from __future__ import annotations

from collections.abc import Callable
from queue import Queue
from typing import Any

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile
from webapp.observable_repo import ObservableInstructorRepo, RepoEvent
from webapp.serializers import as_public_dict


# оборачивает Наблюдателя для инструктора, чтобы мы могли уведомлять подписчиков на события
class InstructorController:
    def __init__(self, repo: ObservableInstructorRepo):
        self._repo = repo

    def count(self) -> int:
        return self._repo.get_count()

    # возвращаются публичные профили
    def list_profiles(self, k: int = 1, n: int | None = None) -> list[PublicInstructorProfile]:
        limit = n if n is not None else max(self.count(), 1)
        return self._repo.get_k_n_short_list(k, limit)

    # возвращаются словари в нужном нам формате для ui
    def list_profiles_payload(self, k: int = 1, n: int | None = None) -> list[dict[str, Any]]:
        return [as_public_dict(p) or {} for p in self.list_profiles(k, n)]

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


__all__ = ["InstructorController"]
