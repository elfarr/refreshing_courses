import json
from typing import Any, cast

from Instructor import Instructor


class PublicInstructorProfile(Instructor):
    def __init__(
        self,
        instructor_id: int | str | dict | Instructor,
        last_name: str | None = None,
        first_name: str | None = None,
        patronymic: str | None = None,
        phone: str | None = None,
        experience_years: int | None = None,
        contact_override: str | None = None,
    ):
        if isinstance(instructor_id, Instructor):
            instr = instructor_id
            super().__init__(
                instr.instructor_id,
                instr.last_name,
                instr.first_name,
                instr.patronymic,
                instr.phone,
                instr.experience_years,
            )
            self.__contact_override = contact_override
            return

        if isinstance(instructor_id, dict):
            d = instructor_id
            super().__init__(
                instructor_id=cast(int, d.get("instructor_id") or d.get("id")),
                last_name=cast(str, d.get("last_name") or d.get("surname") or d.get("last")),
                first_name=cast(str, d.get("first_name") or d.get("first")),
                patronymic=cast(str | None, d.get("patronymic") or d.get("middle_name")),
                phone=cast(str, d.get("phone") or d.get("contact") or d.get("tel")),
                experience_years=cast(int, d.get("experience_years") or d.get("exp")),
            )
            self.__contact_override = cast(str | None, d.get("contact") or d.get("public_contact"))
            return

        if isinstance(instructor_id, str) and last_name is None:
            s = instructor_id.strip()
            if s.startswith("{"):
                d = cast(dict[str, Any], json.loads(s))
                self.__init__(d)  # type: ignore[misc]
                return

            parts = [p.strip() for p in s.split(";")]
            if len(parts) < 6:
                raise ValueError(
                    "Строка должна содержать минимум 6 полей: id;last;first;patronymic;phone;exp"
                )
            pid, last, first, patr, phone, exp, *rest = parts
            super().__init__(int(pid), last, first, None if patr == "" else patr, phone, int(exp))
            self.__contact_override = rest[0] if rest else None
            return

            self.__init__(
                int(pid), last, first, None if patr == "" else patr, phone, int(exp), *rest
            )
            return
        super().__init__(instructor_id, last_name, first_name, patronymic, phone, experience_years)
        self.__contact_override = contact_override

    @property
    def contact(self) -> str:
        return self.__contact_override if self.__contact_override else self.phone

    @contact.setter
    def contact(self, value: str | None) -> None:
        self.__contact_override = None if value is None else self.validate_phone(value)

    @property
    def display_name(self) -> str:
        fi = (self.first_name[:1] + ".") if self.first_name else ""
        pi = (self.patronymic[:1] + ".") if self.patronymic else ""
        return f"{self.last_name} {fi}{pi}".strip()

    def __str__(self) -> str:
        return (
            f"PublicInstructorProfile(id={self.instructor_id}, "
            f"display_name='{self.display_name}', contact='{self.contact}', "
            f"experience_years={self.experience_years})"
        )

    def to_short_string(self) -> str:
        return self.display_name
