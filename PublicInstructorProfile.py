import json
from typing import Optional
from Instructor import Instructor

class PublicInstructorProfile:
    def __init__(self,
                 instructor_id: int,
                 display_name: str,     
                 contact: str,          
                 experience_years: int  
                 ):
        self.instructor_id = instructor_id
        self.display_name = display_name
        self.contact = contact
        self.experience_years = experience_years

    @staticmethod
    def validate_id(value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("instructor_id должен быть положительным целым")
        return value

    @staticmethod
    def validate_display_name(value: str) -> str:
        v = (value or "").strip()
        if v == "":
            raise ValueError("display_name пуст")
        return v

    @staticmethod
    def validate_contact(value: str) -> str:
        v = (value or "").strip()
        if len(v) < 5:
            raise ValueError("contact слишком короткий")
        return v

    @staticmethod
    def validate_experience_years(value: int) -> int:
        if not isinstance(value, int) or value < 0 or value > 80:
            raise ValueError("experience_years должен быть в диапазоне 0..80")
        return value

    @property
    def instructor_id(self) -> int:
        return self.__instructor_id
    @instructor_id.setter
    def instructor_id(self, value: int) -> None:
        self.__instructor_id = PublicInstructorProfile.validate_id(value)

    @property
    def display_name(self) -> str:
        return self.__display_name
    @display_name.setter
    def display_name(self, value: str) -> None:
        self.__display_name = PublicInstructorProfile.validate_display_name(value)

    @property
    def contact(self) -> str:
        return self.__contact
    @contact.setter
    def contact(self, value: str) -> None:
        self.__contact = PublicInstructorProfile.validate_contact(value)

    @property
    def experience_years(self) -> int:
        return self.__experience_years
    @experience_years.setter
    def experience_years(self, value: int) -> None:
        self.__experience_years = PublicInstructorProfile.validate_experience_years(value)

    @classmethod
    def from_instructor(cls, instr: Instructor, contact_override: Optional[str] = None) -> "PublicInstructorProfile":
        fi = (instr.first_name[:1] + ".") if instr.first_name else ""
        pi = (instr.patronymic[:1] + ".") if instr.patronymic else ""
        display = f"{instr.last_name} {fi}{pi}".strip()
        contact = contact_override if contact_override is not None else instr.phone
        return cls(instr.instructor_id, display, contact, instr.experience_years)

    @classmethod
    def from_dict(cls, d: dict) -> "PublicInstructorProfile":
        def pick(*names, default=None):
            for n in names:
                if n in d:
                    return d[n]
            return default
        return cls(
            instructor_id=pick("instructor_id", "id"),
            display_name=pick("display_name", "name"),
            contact=pick("contact", "phone"),
            experience_years=pick("experience_years", "exp"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PublicInstructorProfile":
        return cls.from_dict(json.loads(json_str))

    def __str__(self) -> str:
        return (f"PublicInstructorProfile(id={self.instructor_id}, "
                f"display_name='{self.display_name}', contact='{self.contact}', "
                f"experience_years={self.experience_years})")

    def to_short_string(self) -> str:
        return self.display_name

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, PublicInstructorProfile)
            and (self.display_name, self.contact, self.experience_years)
            == (other.display_name, other.contact, other.experience_years)
        )
