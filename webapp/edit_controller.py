from __future__ import annotations

from typing import Any

from webapp.controller import InstructorController


class EditWindowController:
    def __init__(self, base: InstructorController):
        self._base = base

    def form_config(self, instructor_id: int) -> dict[str, Any]:
        payload = self._base.get_instructor_payload(instructor_id)
        if payload is None:
            raise ValueError("Инструктор не найден")
        return {
            "payload": payload,
            "action": f"/api/edit/{instructor_id}",
            "method": "PUT",
            "title": f"Редактирование #{instructor_id}",
            "subtitle": "Измените поля и сохраните. Главная таблица обновится автоматически.",
            "submit_text": "Сохранить и закрыть",
        }

    def get_instructor_payload(self, instructor_id: int) -> dict[str, Any] | None:
        return self._base.get_instructor_payload(instructor_id)

    def update_instructor(self, instructor_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._base.update_instructor(instructor_id, data)


__all__ = ["EditWindowController"]
