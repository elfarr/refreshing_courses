import json
import re
from typing import Any, cast


class Instructor:
    def __init__(
        self,
        instructor_id: int | str | dict,
        last_name: str | None = None,
        first_name: str | None = None,
        patronymic: str | None = None,
        phone: str | None = None,
        experience_years: int | None = None,
    ):
        if isinstance(instructor_id, dict):
            d = instructor_id
            self.instructor_id = cast(int, d.get("instructor_id") or d.get("id"))
            self.last_name = cast(str, d.get("last_name"))
            self.first_name = cast(str, d.get("first_name"))
            self.patronymic = cast(str | None, d.get("patronymic"))
            self.phone = cast(str, d.get("phone"))
            self.experience_years = cast(int, d.get("experience_years") or d.get("exp"))
            return

        if isinstance(instructor_id, str) and last_name is None:
            s = instructor_id.strip()
            if s.startswith("{"):
                d = json.loads(s)
                self.__init__(d)  # type: ignore[misc]
                return
            parts = [p.strip() for p in s.split(";")]
            if len(parts) != 6:
                raise ValueError(
                    "Строка должна содержать 6 полей: id;last;first;patronymic;phone;exp"
                )
            pid, last, first, patr, phone, exp = parts
            self.__init__(  # type: ignore[misc]
                int(pid), last, first, None if patr == "" else patr, phone, int(exp)
            )
            return

        if isinstance(instructor_id, str):
            instructor_id = int(instructor_id)

        if last_name is None or first_name is None or phone is None or experience_years is None:
            raise TypeError("last_name/first_name/phone/experience_years не могут быть None")

        self.instructor_id = instructor_id  # здесь уже int
        self.last_name = last_name
        self.first_name = first_name
        self.patronymic = patronymic
        self.phone = phone
        self.experience_years = experience_years

    @staticmethod
    def validate_instructor_id(value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("instructor_id должен быть положительным целым числом")
        return value

    @staticmethod
    def validate_name(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field} должен быть строкой")
        v = value.strip()
        if v == "":
            raise ValueError(f"{field} не может быть пустым")
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-'\s]+", v):
            raise ValueError(f"{field} должен содержать только буквы, пробелы, апостроф или дефис")
        return v

    @staticmethod
    def validate_patronymic(value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("patronymic должен быть строкой или None")
        v = value.strip()
        if v == "":
            raise ValueError(
                "patronymic не может быть пустой строкой; используйте None, если отчества нет"
            )
        if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\-'\s]+", v):
            raise ValueError(
                "patronymic должен содержать только буквы, пробелы, апостроф или дефис"
            )
        return v

    @staticmethod
    def validate_phone(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("phone должен быть строкой")
        v = value.strip()
        if not re.fullmatch(r"[0-9+\-\s()]+", v):
            raise ValueError(
                "phone содержит недопустимые символы (разрешены цифры, пробелы, + - ( ))"
            )
        if v.count("+") > 1 or ("+" in v and not v.startswith("+")):
            raise ValueError("phone содержит недопустимый символ '+'")
        digits = re.sub(r"\D", "", v)
        if not (7 <= len(digits) <= 15):
            raise ValueError(
                "phone должен соответствовать формату международного номера (E.164: 7–15 цифр)"
            )
        return v

    @staticmethod
    def validate_experience_years(value: int) -> int:
        if not isinstance(value, int) or value < 0 or value > 80:
            raise ValueError("experience_years должен быть целым числом в диапазоне 0..80")
        return value

    @property
    def instructor_id(self) -> int:
        return self.__instructor_id

    @instructor_id.setter
    def instructor_id(self, value: int) -> None:
        self.__instructor_id = Instructor.validate_instructor_id(value)

    @property
    def last_name(self) -> str:
        return self.__last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        self.__last_name = Instructor.validate_name(value, "last_name")

    @property
    def first_name(self) -> str:
        return self.__first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        self.__first_name = Instructor.validate_name(value, "first_name")

    @property
    def patronymic(self) -> str | None:
        return self.__patronymic

    @patronymic.setter
    def patronymic(self, value: str | None) -> None:
        self.__patronymic = Instructor.validate_patronymic(value)

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, value: str) -> None:
        self.__phone = Instructor.validate_phone(value)

    @property
    def experience_years(self) -> int:
        return self.__experience_years

    @experience_years.setter
    def experience_years(self, value: int) -> None:
        self.__experience_years = Instructor.validate_experience_years(value)

    @classmethod
    def from_string(cls, s: str, sep: str = ";") -> "Instructor":
        parts = [p.strip() for p in s.split(sep)]
        if len(parts) != 6:
            raise ValueError("from_string ожидает 6 полей: id;last;first;patronymic;phone;exp")
        pid, last, first, patr, phone, exp = parts
        patronymic = None if patr == "" else patr
        return cls(int(pid), last, first, patronymic, phone, int(exp))

    @classmethod
    def from_json(cls, json_str: str) -> "Instructor":
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, d: dict) -> "Instructor":
        def pick(*names: str, default: Any = None) -> Any:
            for n in names:
                if n in d:
                    return d[n]
            return default

        return cls(
            instructor_id=pick("instructor_id", "id"),
            last_name=pick("last_name"),
            first_name=pick("first_name"),
            patronymic=pick("patronymic"),
            phone=pick("phone"),
            experience_years=pick("experience_years", "exp"),
        )

    def __str__(self) -> str:
        return (
            f"Instructor(id={self.instructor_id}, "
            f"last_name='{self.last_name}', first_name='{self.first_name}', "
            f"patronymic={repr(self.patronymic)}, phone='{self.phone}', "
            f"experience_years={self.experience_years})"
        )

    def to_short_string(self) -> str:
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def __eq__(self, other: object) -> bool:  # ← типизировали аргумент
        return isinstance(other, Instructor) and (
            self.last_name,
            self.first_name,
            self.patronymic,
            self.experience_years,
        ) == (other.last_name, other.first_name, other.patronymic, other.experience_years)
