import json
import os
from typing import List, Optional

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile

class InstructorRepJson:
    def __init__(self, path: str):
        self.path = path
        ## если нет файла который передали то создаем его и кладем пустой список
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                ## поддержка кириллицы и отступы с каждой новой записью
                json.dump([], f, ensure_ascii=False, indent=2)

    # из файла загружаем объекты
    def _load_raw(self) -> List[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Формат файла: ожидается список объектов")
        return data
    
    # просто запись в json 
    def _save_raw(self, data: List[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _to_dict(self, ins: Instructor) -> dict:
        return {
            "instructor_id": ins.instructor_id,
            "last_name": ins.last_name,
            "first_name": ins.first_name,
            "patronymic": ins.patronymic,
            "phone": ins.phone,
            "experience_years": ins.experience_years,
        }

    # чтение всех значений из файла уже в виде объектов
    def read_all(self) -> List[Instructor]:
        rows = self._load_raw()
        return [Instructor(r) for r in rows]

    # запись всех значений в файл
    def write_all(self, items: List[Instructor]) -> None:
        self._save_raw([self._to_dict(x) for x in items])

    # получить объект по ID
    def get_by_id(self, instructor_id: int) -> Optional[Instructor]:
        rows = self._load_raw()
        for r in rows:
            ## находим по ключу из словаря 
            if int(r.get("instructor_id")) == instructor_id:
                ## выдаем объект который создается распаршенный 
                return Instructor(r)
        return None

    # get_k_n_short_list — страница k (1-based) по n элементов, короткие объекты
    def get_k_n_short_list(self, k: int, n: int) -> list[PublicInstructorProfile]:
        if k <= 0 or n <= 0:
            return []
        items = self.read_all()
        start = (k - 1) * n
        end = start + n
        return [PublicInstructorProfile(i) for i in items[start:end]]

    # сортировать элементы по одному полю (last_name)
    def sort_by_last_name(self, reverse: bool = False) -> List[Instructor]:
        items = self.read_all()
        ## сортируем по кортежу, но сначала фамилия
        items.sort(key=lambda x: (x.last_name.lower(), x.first_name.lower(), x.patronymic or ""), reverse=reverse)
        ## перезаписываем отсортированные
        self.write_all(items)
        return items

    # добавить объек
    def add(self, item: Instructor) -> Instructor:
        rows = self._load_raw()
        max_id = max((int(r.get("instructor_id", 0)) for r in rows), default=0)
        ## новый id находим 
        new_id = max_id + 1
        ## делаем объект
        obj = Instructor(
            new_id,
            item.last_name,
            item.first_name,
            item.patronymic,
            item.phone,
            item.experience_years,
        )
        rows.append(self._to_dict(obj))
        ## записываем в файл новый объект
        self._save_raw(rows)
        return obj

    # заменить элемент списка по ID
    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        rows = self._load_raw()
        replaced = False
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
                replaced = True
                break
        if replaced:
            self._save_raw(rows)
        return replaced

    # удалить элемент списка по ID
    def delete_by_id(self, instructor_id: int) -> bool:
        rows = self._load_raw()
        new_rows = [r for r in rows if int(r.get("instructor_id")) != instructor_id]
        deleted = len(new_rows) != len(rows)
        if deleted:
            self._save_raw(new_rows)
        return deleted

    # получить количество элементов
    def get_count(self) -> int:
        return len(self._load_raw())
