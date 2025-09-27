from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import os

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile

class InstructorRepBase(ABC):
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

    ## методы будут реализованы в наследниках
    @abstractmethod
    def _load_raw(self) -> List[dict]:
        ...

    @abstractmethod
    def _save_raw(self, data: List[dict]) -> None:
        ...

    # из инструктора в словарь - нужно для других методов
    def _to_dict(self, ins: Instructor) -> dict:
        return {
            "instructor_id": ins.instructor_id,
            "last_name": ins.last_name,
            "first_name": ins.first_name,
            "patronymic": ins.patronymic,
            "phone": ins.phone,
            "experience_years": ins.experience_years,
        }

    ## из файла делаем список объектов
    def read_all(self) -> List[Instructor]:
        rows = self._load_raw()
        return [Instructor(r) for r in rows]

    ## в файл записываем список объектов
    def write_all(self, items: List[Instructor]) -> None:
        self._save_raw([self._to_dict(x) for x in items])

    ## из полученного списка словарей получаем по id
    def get_by_id(self, instructor_id: int) -> Instructor | None:
        rows = self._load_raw()
        for r in rows:
            if int(r.get("instructor_id")) == instructor_id:
                return Instructor(r)
        return None

    # возвращаем публичные профили
    def get_k_n_short_list(self, k: int, n: int) -> List[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        items = self.read_all()
        start = (k - 1) * n
        end = start + n
        return [PublicInstructorProfile(i) for i in items[start:end]]

    # сортируем по фамилии/имени/отчеству
    def sort_by_last_name(self, reverse: bool = False) -> List[Instructor]:
        items = self.read_all()
        items.sort(
            key=lambda x: (
                (x.last_name or "").lower(),
                (x.first_name or "").lower(),
                (x.patronymic or "").lower(),
            ),
            reverse=reverse,
        )
        self.write_all(items)
        return items

    def add(self, item: Instructor) -> Instructor:
        rows = self._load_raw()
        max_id = max((int(r.get("instructor_id", 0)) for r in rows), default=0)
        new_id = max_id + 1
        obj = Instructor(
            new_id,
            item.last_name,
            item.first_name,
            item.patronymic,
            item.phone,
            item.experience_years,
        )
        rows.append(self._to_dict(obj))
        self._save_raw(rows)
        return obj

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        rows = self._load_raw()
        for idx, r in enumerate(rows):
            if int(r.get("instructor_id")) == instructor_id:
                obj = Instructor(
                    instructor_id,
                    new_item.last_name,
                    new_item.first_name,
                    new_item.patronymic,
                    new_item.phone,
                    new_item.experience_years,
                )
                rows[idx] = self._to_dict(obj)
                self._save_raw(rows)
                return True
        return False

    def delete_by_id(self, instructor_id: int) -> bool:
        rows = self._load_raw()
        new_rows = [r for r in rows if int(r.get("instructor_id")) != instructor_id]
        deleted = len(new_rows) != len(rows)
        if deleted:
            self._save_raw(new_rows)
        return deleted

    def get_count(self) -> int:
        return len(self._load_raw())
