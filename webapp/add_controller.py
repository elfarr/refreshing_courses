from __future__ import annotations

from typing import Any

from webapp.controller import InstructorController


class AddWindowController:
    def __init__(self, base: InstructorController):
        self._base = base

    def form_config(self) -> dict[str, Any]:
        return {
            "payload": None,
            "action": "/api/add",
            "method": "POST",
            "title": "Добавление инструктора",
            "subtitle": "Заполните форму. После сохранения таблица на главной обновится.",
            "submit_text": "Сохранить и закрыть",
        }

    def create_instructor(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._base.create_instructor(data)


__all__ = ["AddWindowController"]
