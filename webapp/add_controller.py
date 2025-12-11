from __future__ import annotations

from typing import Any

from webapp.controller import InstructorController


class AddWindowController:
    def __init__(self, base: InstructorController):
        self._base = base

    def create_instructor(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._base.create_instructor(data)


__all__ = ["AddWindowController"]
