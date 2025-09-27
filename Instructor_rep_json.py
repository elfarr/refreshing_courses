from __future__ import annotations
import json
import os
from typing import List

from Instructor_rep_base import InstructorRepBase


class InstructorRepJson(InstructorRepBase):
    def __init__(self, path: str):
        super().__init__(path)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_raw(self) -> List[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data is None:
            return []
        if not isinstance(data, list):
            raise ValueError("Формат JSON: ожидается список объектов")
        return data

    def _save_raw(self, data: List[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
