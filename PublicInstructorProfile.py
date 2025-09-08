from typing import Optional
from Instructor import Instructor

class PublicInstructorProfile(Instructor):
    def __init__(self,
                 instructor_id: int,
                 last_name: str,
                 first_name: str,
                 patronymic: Optional[str],
                 phone: str,
                 experience_years: int,
                 contact_override: Optional[str] = None):
        super().__init__(instructor_id, last_name, first_name, patronymic, phone, experience_years)
        self.__contact_override = contact_override

    @property
    def contact(self) -> str:
        return self.__contact_override if self.__contact_override else self.phone

    @contact.setter
    def contact(self, value: Optional[str]) -> None:
        self.__contact_override = None if value is None else self.validate_phone(value)

    @property
    def display_name(self) -> str:
        fi = (self.first_name[:1] + ".") if self.first_name else ""
        pi = (self.patronymic[:1] + ".") if self.patronymic else ""
        return f"{self.last_name} {fi}{pi}".strip()

    def __str__(self) -> str:
        return (f"PublicInstructorProfile(id={self.instructor_id}, "
                f"display_name='{self.display_name}', contact='{self.contact}', "
                f"experience_years={self.experience_years})")

    def to_short_string(self) -> str:
        return self.display_name

    @classmethod
    def from_instructor(cls, instr: Instructor, contact_override: Optional[str] = None) -> "PublicInstructorProfile":
        return cls(instr.instructor_id, instr.last_name, instr.first_name,
                   instr.patronymic, instr.phone, instr.experience_years,
                   contact_override=contact_override)

    @classmethod
    def from_dict(cls, d: dict) -> "PublicInstructorProfile":
        def pick(*names, default=None):
            for n in names:
                if n in d and d[n] is not None:
                    return d[n]
            return default

        instr_id = pick("instructor_id", "id")
        phone = pick("phone", "contact", "tel")
        exp = pick("experience_years", "exp")

        last = pick("last_name", "surname", "last")
        first = pick("first_name", "first")
        patr = pick("patronymic", "middle_name")

        name = pick("display_name", "name")
        if (not last or not first) and name:
            parts = str(name).strip().split()
            if parts:
                last = last or parts[0]
                initials = "".join(parts[1:]) if len(parts) > 1 else ""
                if not first:
                    first = initials[:1] or "?"      
                if not patr and len(initials) >= 2:
                    patr = initials[1:2] or None

        return cls(
            instructor_id=instr_id,
            last_name=last,
            first_name=first,
            patronymic=patr if patr != "" else None,
            phone=phone,
            experience_years=exp,
            contact_override=pick("contact", "public_contact")
        )
