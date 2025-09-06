from typing import Optional

class Instructor:
    def __init__(self,
                 instructor_id: int,
                 last_name: str,
                 first_name: str,
                 patronymic: Optional[str],
                 phone: str,
                 experience_years: int):
        self.__instructor_id = instructor_id
        self.__last_name = last_name
        self.__first_name = first_name
        self.__patronymic = patronymic
        self.__phone = phone
        self.__experience_years = experience_years

    def get_instructor_id(self) -> int:
        return self.__instructor_id

    def get_last_name(self) -> str:
        return self.__last_name

    def get_first_name(self) -> str:
        return self.__first_name

    def get_patronymic(self) -> Optional[str]:
        return self.__patronymic

    def get_phone(self) -> str:
        return self.__phone

    def get_experience_years(self) -> int:
        return self.__experience_years

    def set_instructor_id(self, value: int) -> None:
        self.__instructor_id = value

    def set_last_name(self, value: str) -> None:
        self.__last_name = value

    def set_first_name(self, value: str) -> None:
        self.__first_name = value

    def set_patronymic(self, value: Optional[str]) -> None:
        self.__patronymic = value

    def set_phone(self, value: str) -> None:
        self.__phone = value

    def set_experience_years(self, value: int) -> None:
        self.__experience_years = value
