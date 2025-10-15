from collections.abc import Callable
from typing import Any

from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile


def run_case(title: str, fn: Callable[[], object], should_fail: bool = False) -> None:
    try:
        obj = fn()
        if should_fail:
            print(f"\n[FAIL] {title} -> ожидалась ошибка, но её нет")
        else:
            print(f"\n[OK] {title}")
            if isinstance(obj, Instructor) or isinstance(obj, PublicInstructorProfile):
                print("  full: ", str(obj))
                print("  short:", obj.to_short_string())
    except Exception as e:
        if should_fail:
            print(f"\n[OK] {title} -> поймали ожидаемую ошибку: {e}")
        else:
            print(f"\n[FAIL] {title} -> не ожидал ошибку: {e}")


def make(*args: Any, **kwargs: Any) -> Callable[[], Instructor]:
    return lambda: Instructor(*args, **kwargs)


if __name__ == "__main__":
    cases = [
        (
            "Создание корректного Instructor",
            make(1, "Иванов", "Иван", "Иванович", "+79001234567", 5),
            False,
        ),
        ("Отрицательный instructor_id", make(-1, "Иванов", "Иван", None, "+79991112233", 3), True),
        ("Пустая фамилия", make(1, "   ", "Иван", None, "+79991112233", 3), True),
        ("Пустое имя", make(1, "Иванов", "   ", None, "+79991112233", 3), True),
        (
            "Пустая строка как отчество (нужно None)",
            make(1, "Иванов", "Иван", "   ", "+79991112233", 3),
            True,
        ),
        ("Короткий телефон", make(1, "Иванов", "Иван", None, "123", 3), True),
        (
            "Телефон с недопустимыми символами",
            make(1, "Иванов", "Иван", None, "+79991112233ext5", 3),
            True,
        ),
        ("Опыт отрицательный", make(1, "Иванов", "Иван", None, "+79991112233", -2), True),
        ("Опыт > 80 лет", make(1, "Иванов", "Иван", None, "+79991112233", 120), True),
        ("from_string OK", (lambda: Instructor("2;Петров;Пётр;;+79011112233;3")), False),
        ("from_string BAD (мало полей)", (lambda: Instructor("2;Петров;Пётр")), True),
        (
            "from_json OK (базовые ключи)",
            (
                lambda: Instructor(
                    '{"instructor_id":3,"last_name":"Сидоров","first_name":"Сидор","patronymic":null,"phone":"+79023334455","experience_years":10}'
                )
            ),
            False,
        ),
        (
            "from_json OK (синонимы id/exp)",
            (
                lambda: Instructor(
                    '{"id":4,"last_name":"Кузнецов","first_name":"Денис","phone":"+79035556677","exp":1}'
                )
            ),
            False,
        ),
        ("from_json BAD (битый json)", (lambda: Instructor('{"id": "не число"')), True),
        (
            "from_dict BAD (нет last_name)",
            (
                lambda: Instructor(
                    {"id": 6, "first_name": "Юрий", "phone": "+79050000000", "exp": 2}
                )
            ),
            True,
        ),
        ("demo test", (lambda: Instructor("2;Петров;Пётр;;+7901111@@@2233;3")), True),
    ]

    for title, fn, should_fail in cases:
        run_case(title, fn, should_fail)

    print("\nСравнение на равенство (по ФИО + стаж):")
    a = Instructor(10, "Иванов", "Иван", "Иванович", "+79000000000", 5)
    b = Instructor(999, "Иванов", "Иван", "Иванович", "+79999999999", 5)
    c = Instructor(1000, "Иванов", "Иван", "Иванович", "+79000000000", 6)

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
    pub_a = PublicInstructorProfile(a)
    pub_b = PublicInstructorProfile(b, contact_override="+79111111111")
    pub_c = PublicInstructorProfile(
        {
            "id": 1000,
            "last_name": "Иванов",
            "first_name": "Иван",
            "patronymic": "Иванович",
            "phone": "+79000000000",
            "exp": 6,
        }
    )

    print("pub_a full:  ", pub_a)
    print("pub_a short: ", pub_a.to_short_string())
    print("pub_b full:  ", pub_b)
    print("pub_b short: ", pub_b.to_short_string())
    print("pub_c full:  ", pub_c)
    print("pub_c short: ", pub_c.to_short_string())

    print("\nСравнение публичных профилей (display_name + contact + exp):")
    print("  pub_a == pub_b ?", pub_a == pub_b)
    print("  pub_a == pub_c ?", pub_a == pub_c)
