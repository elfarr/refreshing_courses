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
    ]

    for title, fn, should_fail in cases:
        run_case(title, fn, should_fail)
