from Instructor import Instructor
from adapters import JsonRepoAdapter, YamlRepoAdapter, DbRepoAdapter
from instructor_repo_iface import InstructorRepo

def clear_repo(repo: InstructorRepo) -> None:
    while True:
        page = repo.get_k_n_short_list(1, 1000)  
        if not page:
            break
        for p in page:
            repo.delete_by_id(p.instructor_id)

def smoke(repo: InstructorRepo, label: str):
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

if __name__ == "__main__":
    smoke(JsonRepoAdapter("instructors.json"), "JSON (adapter)")
    smoke(YamlRepoAdapter("instructors.yaml"), "YAML (adapter)")
    smoke(DbRepoAdapter(host="localhost", port=5432, dbname="postgres", user="postgres", password="1234"),
          "DB (adapter)")
