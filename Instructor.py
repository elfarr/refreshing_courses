from typing import Optional

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
