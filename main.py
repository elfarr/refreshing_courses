from Instructor import Instructor

def show_ok(title: str, fn):
    try:
        fn()
        print(f"[OK] {title}")
    except Exception as e:
        print(f"[FAIL] {title} -> не ожидал ошибку: {e}")

def show_fail(title: str, fn):
    try:
        fn()
        print(f"[FAIL] {title} -> ожидалась ошибка, но её нет")
    except Exception as e:
        print(f"[OK] {title} -> поймали ожидаемую ошибку: {e}")

if __name__ == "__main__":
    def create_valid():
        instr = Instructor(
            instructor_id=1,
            last_name="Иванов",
            first_name="Иван",
            patronymic="Иванович",
            phone="+7 (900) 123-45-67",
            experience_years=5
        )

    show_ok("Создание корректного Instructor", create_valid)

    show_fail("Отрицательный instructor_id",
              lambda: Instructor(-1, "Иванов", "Иван", None, "+7 999 111-22-33", 3))

    show_fail("Пустая фамилия",
              lambda: Instructor(1, "   ", "Иван", None, "+7 999 111-22-33", 3))

    show_fail("Пустое имя",
              lambda: Instructor(1, "Иванов", "   ", None, "+7 999 111-22-33", 3))

    show_fail("Пустая строка как отчество (должно быть None, если нет)",
              lambda: Instructor(1, "Иванов", "Иван", "   ", "+7 999 111-22-33", 3))

    show_fail("Короткий телефон",
              lambda: Instructor(1, "Иванов", "Иван", None, "123", 3))

    show_fail("Телефон с недопустимыми символами",
              lambda: Instructor(1, "Иванов", "Иван", None, "+7 999 111-22-33 ext.5", 3))

    show_fail("Опыт отрицательный",
              lambda: Instructor(1, "Иванов", "Иван", None, "+7 999 111-22-33", -2))

    show_fail("Опыт > 80 лет",
              lambda: Instructor(1, "Иванов", "Иван", None, "+7 999 111-22-33", 120))
