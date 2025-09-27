from __future__ import annotations
import os
from typing import List

import yaml 
from Instructor_rep_base import InstructorRepBase


class InstructorRepYaml(InstructorRepBase):
    def __init__(self, path: str):
        super().__init__(path)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.safe_dump([], f, allow_unicode=True, sort_keys=False, indent=2)

    def _load_raw(self) -> List[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return []
        if not isinstance(data, list):
            raise ValueError("Формат YAML: ожидается список объектов")
        return data

    def _save_raw(self, data: List[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, indent=2)
