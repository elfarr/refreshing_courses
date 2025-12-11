from __future__ import annotations

from typing import Any

from webapp.controller import InstructorController


class EditWindowController:
    def __init__(self, base: InstructorController):
        self._base = base

    def get_instructor_payload(self, instructor_id: int) -> dict[str, Any] | None:
        return self._base.get_instructor_payload(instructor_id)

    def update_instructor(self, instructor_id: int, data: dict[str, Any]) -> dict[str, Any]:
        return self._base.update_instructor(instructor_id, data)


__all__ = ["EditWindowController"]
