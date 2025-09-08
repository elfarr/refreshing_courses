from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile 

def run_case(title: str, fn, should_fail: bool = False) -> None:
    try:
        obj = fn()
        if should_fail:
            print(f"[FAIL] {title} -> ожидалась ошибка, но её нет")
        else:
            print(f"[OK] {title}")
            if isinstance(obj, Instructor):
                print("  full: ", str(obj))
                print("  short:", obj.to_short_string())
            elif isinstance(obj, PublicInstructorProfile):
                print("  full: ", str(obj))
                print("  short:", obj.to_short_string())
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

    print("\nСравнение на равенство (по ФИО + стаж):")
    a = Instructor(10, "Иванов", "Иван", "Иванович", "+7 900 000-00-00", 5)
    b = Instructor(999, "Иванов", "Иван", "Иванович", "+7 999 999-99-99", 5)
    c = Instructor(1000, "Иванов", "Иван", "Иванович", "+7 900 000-00-00", 6)

    print("a full:  ", a)
    print("a short: ", a.to_short_string())
    print("b full:  ", b)
    print("b short: ", b.to_short_string())
    print("c full:  ", c)
    print("c short: ", c.to_short_string())

    print("\nРезультаты сравнения:")
    print("  a == b ?", a == b)
    print("  a == c ?", a == c)

    print("\nПубличный профиль (короткая версия):")
    pub_a = PublicInstructorProfile.from_instructor(a)
    pub_b = PublicInstructorProfile.from_instructor(b, contact_override="+7 911 111-11-11")
    pub_c = PublicInstructorProfile.from_dict({
        "id": 1000,
        "name": "Иванов И.И.",
        "phone": "+7 900 000-00-00",
        "exp": 6
    })

    print("pub_a full:  ", pub_a)
    print("pub_a short: ", pub_a.to_short_string())
    print("pub_b full:  ", pub_b)
    print("pub_b short: ", pub_b.to_short_string())
    print("pub_c full:  ", pub_c)
    print("pub_c short: ", pub_c.to_short_string())

    print("\nСравнение публичных профилей (display_name + contact + exp):")
    print("  pub_a == pub_b ?", pub_a == pub_b)
    print("  pub_a == pub_c ?", pub_a == pub_c)
