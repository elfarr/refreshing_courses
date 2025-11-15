from __future__ import annotations

import json

import yaml  # type: ignore[import-untyped]

from adapters import DbRepoAdapter, JsonRepoAdapter, YamlRepoAdapter
from file_repo_decorator import FileFilterSortDecorator
from file_spec import FileQuerySpec
from Instructor import Instructor
from Instructor_rep_json import InstructorRepJson
from Instructor_rep_yaml import InstructorRepYaml
from instructor_repo_iface import InstructorRepo
from PublicInstructorProfile import PublicInstructorProfile
from repo_decorators import DbFilterSortDecorator
from spec import QuerySpec


def pp(title: str, items: list[PublicInstructorProfile]) -> None:
    print(title, [p.to_short_string() for p in items])


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

    asc = repo.sort_by_last_name(False)
    print("sorted by last_name ASC:", [f"{x.last_name} {x.first_name}" for x in asc])

    desc = repo.sort_by_last_name(True)
    print("sorted by last_name DESC:", [f"{x.last_name} {x.first_name}" for x in desc])

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
    base.add(Instructor(14, "Абрамов", "Илья", None, "+79000000014", 6))

    deco = DbFilterSortDecorator(base)

    print("количество (без фильтров):", deco.get_count())
    pp("пагинация (как есть):", deco.get_k_n_short_list(1, 10))

    spec_filtered = QuerySpec(
        where="experience_years >= %s AND last_name ILIKE %s",
        params=(5, "Ив%"),
        order_by="last_name ASC, first_name ASC, COALESCE(patronymic,'') ASC",
    )
    print("количество ('Ив..', опыт>=5):", deco.get_count(spec_filtered))
    pp("пагинация ('Ив..', опыт>=5, FIO ASC):", deco.get_k_n_short_list(1, 10, spec_filtered))


def smoke_files_with_decorator() -> None:
    print("=== JSON (adapter + file decorator) ===")
    j = JsonRepoAdapter("instructors.json")
    clear_repo(j)
    j.add(Instructor(20, "Иванов", "Иван", "Иванович", "+79000000020", 5))
    j.add(Instructor(21, "Петров", "Пётр", None, "+79000000021", 3))
    j.add(Instructor(22, "Сидорова", "Анна", None, "+79000000022", 7))
    j.add(Instructor(23, "Иванова", "Алёна", None, "+79000000023", 9))
    j.add(Instructor(24, "Абрамов", "Илья", None, "+79000000024", 6))
    fj = FileFilterSortDecorator(j)

    print("количество (без фильтров):", fj.get_count())
    pp("пагинация (как есть):", fj.get_k_n_short_list(1, 10))

    # 1) ФИО ASC
    f_sort_fio_asc = FileQuerySpec(
        predicate=lambda x: True,
        key=lambda x: ((x.last_name or ""), (x.first_name or ""), (x.patronymic or "")),
        reverse=False,
    )
    pp("пагинация (FIO ASC):", fj.get_k_n_short_list(1, 10, f_sort_fio_asc))

    # 2) ФИО DESC
    f_sort_fio_desc = FileQuerySpec(
        predicate=lambda x: True,
        key=lambda x: ((x.last_name or ""), (x.first_name or ""), (x.patronymic or "")),
        reverse=True,
    )
    pp("пагинация (FIO DESC):", fj.get_k_n_short_list(1, 10, f_sort_fio_desc))

    # 3) Фильтр + сортировка по стажу DESC, затем ФИО ASC (две страницы)
    f_exp_desc_then_ln = FileQuerySpec(
        predicate=lambda x: x.experience_years >= 5,
        key=lambda x: (
            -x.experience_years,
            (x.last_name or ""),
            (x.first_name or ""),
            (x.patronymic or ""),
        ),
        reverse=False,
    )
    print("количество (стаж>=5):", fj.get_count(f_exp_desc_then_ln))
    pp(
        "пагинация (стаж>=5, стаж DESC, затем ФИО ASC) стр.1:",
        fj.get_k_n_short_list(1, 2, f_exp_desc_then_ln),
    )
    pp(
        "пагинация (стаж>=5, стаж DESC, затем ФИО ASC) стр.2:",
        fj.get_k_n_short_list(2, 2, f_exp_desc_then_ln),
    )

    print("=== YAML (adapter + file decorator) ===")
    y = YamlRepoAdapter("instructors.yaml")
    clear_repo(y)
    y.add(Instructor(30, "Смирнов", "Лев", None, "+79000000030", 2))
    y.add(Instructor(31, "Абрамов", "Илья", None, "+79000000031", 6))
    y.add(Instructor(32, "Баранова", "Вера", None, "+79000000032", 8))
    y.add(Instructor(33, "Иванов", "Олег", None, "+79000000033", 5))

    fy = FileFilterSortDecorator(y)

    f_AB_exp_desc = FileQuerySpec(
        predicate=lambda x: (x.last_name or "").startswith(("А", "Б")),
        key=lambda x: (-x.experience_years, (x.last_name or ""), (x.first_name or "")),
        reverse=False,
    )
    print("количество (фамилии А/Б):", fy.get_count(f_AB_exp_desc))
    pp("пагинация (А/Б, стаж DESC, затем ФИО ASC):", fy.get_k_n_short_list(1, 10, f_AB_exp_desc))

    f_AB_fio_asc = FileQuerySpec(
        predicate=lambda x: (x.last_name or "").startswith(("А", "Б")),
        key=lambda x: ((x.last_name or ""), (x.first_name or "")),
        reverse=False,
    )
    pp("пагинация (А/Б, FIO ASC):", fy.get_k_n_short_list(1, 10, f_AB_fio_asc))


def demo_invalid_data_loading() -> None:
    print("=== INVALID DATA DEMO: JSON/YAML ===")

    bad_json_path = "instructors_invalid.json"
    bad_json_data = [
        # invalid: отрицательный id
        {
            "instructor_id": -1,
            "last_name": "Иванов",
            "first_name": "Иван",
            "patronymic": "Иванович",
            "phone": "+79000000000",
            "experience_years": 5,
        },
        # invalid: цифра в фамилии
        {
            "instructor_id": 2,
            "last_name": "Петров1",
            "first_name": "Пётр",
            "patronymic": None,
            "phone": "+7 900 000 00 01",
            "experience_years": 3,
        },
        # invalid: пустая строка в patronymic
        {
            "instructor_id": 3,
            "last_name": "Сидорова",
            "first_name": "Анна",
            "patronymic": "",
            "phone": "+7(900)000-0002",
            "experience_years": 7,
        },
        # invalid: телефон "abc"
        {
            "instructor_id": 4,
            "last_name": "Смирнов",
            "first_name": "Лев",
            "patronymic": None,
            "phone": "abc",
            "experience_years": 2,
        },
        # invalid: exp > 80
        {
            "instructor_id": 5,
            "last_name": "Иванова",
            "first_name": "Алёна",
            "patronymic": None,
            "phone": "+79000000005",
            "experience_years": 120,
        },
        # valid: альтернативные ключи id/exp
        {"id": 6, "last_name": "Абрамов", "first_name": "Илья", "phone": "+79000000006", "exp": 6},
    ]
    with open(bad_json_path, "w", encoding="utf-8") as f:
        json.dump(bad_json_data, f, ensure_ascii=False, indent=2)

    bad_yaml_path = "instructors_invalid.yaml"
    bad_yaml_data = [
        {
            "instructor_id": 1,
            "last_name": "Абрамов",
            "first_name": "Илья",
            "phone": "+79000000001",
            "experience_years": 6,
        },
        {
            "instructor_id": 0,
            "last_name": "Иванов",
            "first_name": "Иван",
            "patronymic": "Иванович",
            "phone": "+79000000002",
            "experience_years": 5,
        },  # invalid id=0
        {
            "instructor_id": 3,
            "last_name": "Баранова",
            "first_name": "Вера",
            "patronymic": None,
            "phone": "+79000000003",
            "experience_years": -1,
        },  # invalid exp<0
        {
            "instructor_id": 4,
            "last_name": "Сидорова2",
            "first_name": "Анна",
            "patronymic": None,
            "phone": "+79000000004",
            "experience_years": 7,
        },  # invalid фамилия
        {
            "instructor_id": 5,
            "last_name": "Смирнов",
            "first_name": "",
            "patronymic": None,
            "phone": "+79000000005",
            "experience_years": 2,
        },  # invalid пустое имя
    ]
    with open(bad_yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(bad_yaml_data, f, allow_unicode=True, sort_keys=False, indent=2)

    print("\n[JSON] Пытаемся repo.read_all() целиком (ожидается ошибка):")
    jrepo = InstructorRepJson(bad_json_path)
    try:
        _ = jrepo.read_all()
        print("ОК: неожиданно файл загрузился без ошибок.")
    except Exception as e:
        print(f"ОЖИДАЕМАЯ ОШИБКА: {e}")

    print("\n[YAML] Пытаемся repo.read_all() целиком (ожидается ошибка):")
    yrepo = InstructorRepYaml(bad_yaml_path)
    try:
        _ = yrepo.read_all()
        print("ОК: неожиданно файл загрузился без ошибок.")
    except Exception as e:
        print(f"ОЖИДАЕМАЯ ОШИБКА: {e}")

    print("\n[JSON] Построчная проверка записей:")
    with open(bad_json_path, encoding="utf-8") as f:
        raw_json = json.load(f)
    for i, obj in enumerate(raw_json, start=1):
        try:
            ins = Instructor(obj)
            print(f"  #{i}: OK -> {ins.to_short_string()}")
        except Exception as e:
            print(f"  #{i}: ERROR -> {e} | data={obj}")

    print("\n[YAML] Построчная проверка записей:")
    with open(bad_yaml_path, encoding="utf-8") as f:
        raw_yaml = yaml.safe_load(f) or []
    for i, obj in enumerate(raw_yaml, start=1):
        try:
            ins = Instructor(obj)
            print(f"  #{i}: OK -> {ins.to_short_string()}")
        except Exception as e:
            print(f"  #{i}: ERROR -> {e} | data={obj}")


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

    demo_invalid_data_loading()
