from __future__ import annotations

from typing import Any, cast

from file_spec import FileQuerySpec
from Instructor import Instructor
from instructor_repo_iface import InstructorRepo
from PublicInstructorProfile import PublicInstructorProfile


class FileFilterSortDecorator(InstructorRepo):
    def __init__(self, base_repo: InstructorRepo):
        self._repo = base_repo

    # прокидываем базовые операции как есть
    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._repo.get_by_id(instructor_id)

    def add(self, item: Instructor) -> Instructor:
        return self._repo.add(item)

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        return self._repo.replace_by_id(instructor_id, new_item)

    def delete_by_id(self, instructor_id: int) -> bool:
        return self._repo.delete_by_id(instructor_id)

    def _read_all(self) -> list:
        if hasattr(self._repo, "read_all") and callable(self._repo.read_all):
            return cast(list[Any], self._repo.read_all())
        # через пагинацию достаем если нет метода
        items: list[Any] = []
        if hasattr(self._repo, "get_k_n_short_list") and callable(self._repo.get_k_n_short_list):
            k, n = 1, 1000  # достаточно крупный батч
            while True:
                page = self._repo.get_k_n_short_list(k, n)
                if not page:
                    break
                items.extend(page)
                k += 1
        return items

    def _to_public(self, x: Any) -> PublicInstructorProfile:
        return x if isinstance(x, PublicInstructorProfile) else PublicInstructorProfile(x)

    def get_count(self, spec: FileQuerySpec | None = None) -> int:
        items = self._read_all()
        if spec and spec.predicate:
            items = [x for x in items if spec.predicate(x)]
        return len(items)

    def get_k_n_short_list(
        self, k: int, n: int, spec: FileQuerySpec | None = None
    ) -> list[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        items = self._read_all()

        if spec and spec.predicate:
            items = [x for x in items if spec.predicate(x)]
        if spec and spec.key:
            items = sorted(items, key=spec.key, reverse=spec.reverse)
        else:
            items = sorted(
                items,
                key=lambda x: (x.last_name, x.first_name, (x.patronymic or ""), x.instructor_id),
            )

        start = (k - 1) * n
        page = items[start : start + n]
        return [self._to_public(i) for i in page]

    def sort_by_last_name(self, reverse: bool = False) -> list[Instructor]:
        # если базовый репозиторий умеет сам — делегируем
        base_sort = getattr(self._repo, "sort_by_last_name", None)
        return cast(list[Instructor], base_sort(reverse=reverse))  # type: ignore[misc]
