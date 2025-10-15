from adapters import DbRepoAdapter, JsonRepoAdapter, YamlRepoAdapter
from file_repo_decorator import FileFilterSortDecorator
from file_spec import FileQuerySpec
from Instructor import Instructor
from instructor_repo_iface import InstructorRepo
from repo_decorators import DbFilterSortDecorator
from spec import QuerySpec


def clear_repo(repo: InstructorRepo) -> None:
    while True:
        page = repo.get_k_n_short_list(1, 1000)
        if not page:
            break
        for p in page:
            repo.delete_by_id(p.instructor_id)


def smoke(repo: InstructorRepo, label: str) -> None:
    print(f"=== {label} ===")
    clear_repo(repo)
    a = repo.add(Instructor(1, "Иванов", "Иван", "Иванович", "+79000000001", 5))
    b = repo.add(Instructor(2, "Петров", "Пётр", None, "+79000000002", 3))
    c = repo.add(Instructor(3, "Сидорова", "Анна", None, "+79000000003", 7))

    print("count:", repo.get_count())
    print("by_id:", repo.get_by_id(a.instructor_id))
    print("page k=1, n=2:", [p.to_short_string() for p in repo.get_k_n_short_list(1, 2)])

    b2 = Instructor(b.instructor_id, "Петров", "Пётр", "Петрович", "+79000000022", 4)
    print("replaced:", repo.replace_by_id(b.instructor_id, b2))
    print("deleted:", repo.delete_by_id(c.instructor_id))
    print("final count:", repo.get_count())


def smoke_db_with_decorator() -> None:
    print("=== DB (adapter + decorator) ===")
    base = DbRepoAdapter(
        host="localhost", port=5432, dbname="postgres", user="postgres", password="1234"
    )
    clear_repo(base)

    base.add(Instructor(10, "Иванов", "Иван", "Иванович", "+79000000010", 5))
    base.add(Instructor(11, "Петров", "Пётр", None, "+79000000011", 3))
    base.add(Instructor(12, "Сидорова", "Анна", None, "+79000000012", 7))
    base.add(Instructor(13, "Иванова", "Алёна", None, "+79000000013", 9))

    deco = DbFilterSortDecorator(base)

    print("количество (без фильтров):", deco.get_count())
    print(
        "пагинация (без фильтров):", [p.to_short_string() for p in deco.get_k_n_short_list(1, 10)]
    )

    spec = QuerySpec(
        where="experience_years >= %s AND last_name ILIKE %s",
        params=(5, "Ив%"),
        order_by="last_name ASC, first_name ASC",
    )
    print("количество ('Ив..', опыт>=5):", deco.get_count(spec))
    print(
        "пагинация ('Ив..', опыт>=5):",
        [p.to_short_string() for p in deco.get_k_n_short_list(1, 10, spec)],
    )

    spec2 = QuerySpec(
        where="patronymic IS NULL", params=(), order_by="experience_years DESC, last_name ASC"
    )
    print("количество (без отчества):", deco.get_count(spec2))
    print(
        "пагинация (без отчества)):",
        [p.to_short_string() for p in deco.get_k_n_short_list(1, 10, spec2)],
    )


# === демонстрация декоратора для файловых репозиториев (JSON/YAML) ===
def smoke_files_with_decorator() -> None:
    print("=== JSON (adapter + file decorator) ===")
    j = JsonRepoAdapter("instructors.json")
    clear_repo(j)
    j.add(Instructor(20, "Иванов", "Иван", "Иванович", "+79000000020", 5))
    j.add(Instructor(21, "Петров", "Пётр", None, "+79000000021", 3))
    j.add(Instructor(22, "Сидорова", "Анна", None, "+79000000022", 7))
    j.add(Instructor(23, "Иванова", "Алёна", None, "+79000000023", 9))
    fj = FileFilterSortDecorator(j)

    print("количество (без фильтров):", fj.get_count())
    print("пагинация (без фильтров):", [p.to_short_string() for p in fj.get_k_n_short_list(1, 10)])

    f_spec = FileQuerySpec(
        predicate=lambda x: x.experience_years >= 5 and x.last_name.startswith("Ив"),
        key=lambda x: (x.last_name, x.first_name),
        reverse=False,
    )
    print("количество (Ив*, стаж>=5):", fj.get_count(f_spec))
    print(
        "пагинация (Ив*, стаж>=5):",
        [p.to_short_string() for p in fj.get_k_n_short_list(1, 10, f_spec)],
    )

    print("=== YAML (adapter + file decorator) ===")
    y = YamlRepoAdapter("instructors.yaml")
    clear_repo(y)
    y.add(Instructor(30, "Смирнов", "Лев", None, "+79000000030", 2))
    y.add(Instructor(31, "Абрамов", "Илья", None, "+79000000031", 6))
    y.add(Instructor(32, "Баранова", "Вера", None, "+79000000032", 8))

    fy = FileFilterSortDecorator(y)

    f_spec2 = FileQuerySpec(
        predicate=lambda x: x.last_name.startswith(("А", "Б")),
        key=lambda x: x.experience_years,
        reverse=True,
    )
    print("количество (фамилии А/Б):", fy.get_count(f_spec2))
    print(
        "пагинация (фамилии А/Б, стаж DESC):",
        [p.to_short_string() for p in fy.get_k_n_short_list(1, 10, f_spec2)],
    )


if __name__ == "__main__":
    smoke(JsonRepoAdapter("instructors.json"), "JSON (adapter)")
    smoke(YamlRepoAdapter("instructors.yaml"), "YAML (adapter)")
    smoke(
        DbRepoAdapter(
            host="localhost", port=5432, dbname="postgres", user="postgres", password="1234"
        ),
        "DB (adapter)",
    )
    smoke_db_with_decorator()
    smoke_files_with_decorator()
