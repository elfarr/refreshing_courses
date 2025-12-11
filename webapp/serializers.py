from __future__ import annotations

from typing import Any

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile


# нужно чтобы сериализовывать и инструктора и его публичный профиль, добавляет те поля, которых нет в обчных классах
def as_public_dict(item: Instructor | PublicInstructorProfile | None) -> dict[str, Any] | None:
    if item is None:
        return None
    profile = item if isinstance(item, PublicInstructorProfile) else PublicInstructorProfile(item)
    return {
        "instructor_id": profile.instructor_id,
        "last_name": profile.last_name,
        "first_name": profile.first_name,
        "patronymic": profile.patronymic,
        "phone": profile.phone,
        "experience_years": profile.experience_years,
        "display_name": profile.display_name,
        "contact": profile.contact,
    }
