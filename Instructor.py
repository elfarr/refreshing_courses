import json
from typing import Optional, Iterable

class Instructor:
    def __init__(self,
                 instructor_id: int,
                 last_name: str,
                 first_name: str,
                 patronymic: Optional[str],
                 phone: str,
                 experience_years: int):
        self.instructor_id = instructor_id
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
        return v

    @staticmethod
    def validate_patronymic(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("patronymic должен быть строкой или None")
        v = value.strip()
        if v == "":
            raise ValueError("patronymic не может быть пустой строкой; используйте None, если отчества нет")
        return v

    @staticmethod
    def validate_phone(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("phone должен быть строкой")
        v = value.strip()
        if len(v) < 5:
            raise ValueError("phone слишком короткий")
        allowed = set("+ -()0123456789")
        if any(ch not in allowed for ch in v):
            raise ValueError("phone содержит недопустимые символы (разрешены цифры, пробел, + - ( ))")
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
    def patronymic(self) -> Optional[str]:
        return self.__patronymic

    @patronymic.setter
    def patronymic(self, value: Optional[str]) -> None:
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
        def pick(*names, default=None):
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

    @classmethod
    def from_csv_row(cls, row: Iterable[str]) -> "Instructor":
        parts = [str(x).strip() for x in row]
        if len(parts) != 6:
            raise ValueError("from_csv_row ожидает ровно 6 столбцов")
        pid, last, first, patr, phone, exp = parts
        patronymic = None if patr == "" else patr
        return cls(int(pid), last, first, patronymic, phone, int(exp))
