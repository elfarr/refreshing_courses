from Instructor import Instructor

def run_case(title: str, fn, should_fail: bool = False) -> None:
    try:
        fn()
        if should_fail:
            print(f"[FAIL] {title} -> ожидалась ошибка, но её нет")
        else:
            print(f"[OK] {title}")
    except Exception as e:
        if should_fail:
            print(f"[OK] {title} -> поймали ожидаемую ошибку: {e}")
        else:
            print(f"[FAIL] {title} -> не ожидал ошибку: {e}")

def make(*args, **kwargs):
    return lambda: Instructor(*args, **kwargs)

if __name__ == "__main__":
    cases = [
        ("Создание корректного Instructor",
         make(1, "Иванов", "Иван", "Иванович", "+7 (900) 123-45-67", 5), False),

        ("Отрицательный instructor_id",
         make(-1, "Иванов", "Иван", None, "+7 999 111-22-33", 3), True),

        ("Пустая фамилия",
         make(1, "   ", "Иван", None, "+7 999 111-22-33", 3), True),

        ("Пустое имя",
         make(1, "Иванов", "   ", None, "+7 999 111-22-33", 3), True),

        ("Пустая строка как отчество (нужно None)",
         make(1, "Иванов", "Иван", "   ", "+7 999 111-22-33", 3), True),

        ("Короткий телефон",
         make(1, "Иванов", "Иван", None, "123", 3), True),

        ("Телефон с недопустимыми символами",
         make(1, "Иванов", "Иван", None, "+7 999 111-22-33 ext.5", 3), True),

        ("Опыт отрицательный",
         make(1, "Иванов", "Иван", None, "+7 999 111-22-33", -2), True),

        ("Опыт > 80 лет",
         make(1, "Иванов", "Иван", None, "+7 999 111-22-33", 120), True),

        ("from_string OK",
         (lambda: Instructor.from_string("2;Петров;Пётр;;+7 (901) 111-22-33;3")), False),

        ("from_string BAD (мало полей)",
         (lambda: Instructor.from_string("2;Петров;Пётр")), True),

        ("from_json OK (базовые ключи)",
         (lambda: Instructor.from_json('{"instructor_id":3,"last_name":"Сидоров","first_name":"Сидор","patronymic":null,"phone":"+7 902 333-44-55","experience_years":10}')), False),

        ("from_json OK (синонимы id/exp)",
         (lambda: Instructor.from_json('{"id":4,"last_name":"Кузнецов","first_name":"Денис","phone":"+7 903 555-66-77","exp":1}')), False),

        ("from_json BAD (битый json)",
         (lambda: Instructor.from_json('{"id": "не число"')), True),

        ("from_dict OK (синонимы id/exp)",
         (lambda: Instructor.from_dict({"id": 5, "last_name": "Новиков", "first_name": "Олег", "patronymic": "", "phone": "+7 904 777-88-99", "exp": 6})), False),

        ("from_dict BAD (нет last_name)",
         (lambda: Instructor.from_dict({"id": 6, "first_name": "Юрий", "phone": "+7 905 000-00-00", "exp": 2})), True),
    ]

    for title, fn, should_fail in cases:
        run_case(title, fn, should_fail)
