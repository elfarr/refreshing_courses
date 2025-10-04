from Instructor import Instructor
from Instructor_rep_json import InstructorRepJson
from Instructor_rep_yaml import InstructorRepYaml
from Instructor_rep_db import InstructorRepDB  # репозиторий на чистых SQL

def smoke(repo):
    # очищаем на всякий случай
    repo.write_all([])
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

def smoke_db():
    # подключение к бд
    cfg = dict(host="localhost", port=5432, dbname="postgres", user="postgres", password="1234")
    # создаем объект для работы с бд 
    repo = InstructorRepDB(**cfg)
    try:
        a = repo.add(Instructor(4, "Иванов", "Иван", "Иванович", "+79000000001", 5)) 
        b = repo.add(Instructor(5, "Петров", "Пётр", None, "+79000000002", 3))       
        c = repo.add(Instructor(6, "Сидорова", "Анна", None, "+79000000003", 7))      

        print("[DB] count:", repo.get_count()) 
        print("[DB] by_id:", repo.get_by_id(5)) 
        print("[DB] page k=1, n=2:", [p.to_short_string() for p in repo.get_k_n_short_list(1, 2)]) 

        b2 = Instructor(b.instructor_id, "Петров", "Пётр", "Петрович", "+79000000022", 4)
        print("[DB] replaced:", repo.replace_by_id(b.instructor_id, b2))  
        print("[DB] deleted:", repo.delete_by_id(c.instructor_id))        
        print("[DB] final count:", repo.get_count())                      
    finally:
        repo.close()

if __name__ == "__main__":
    print("=== JSON ===")
    smoke(InstructorRepJson("instructors.json"))

    print("\n=== YAML ===")
    smoke(InstructorRepYaml("instructors.yaml"))

    print("\n=== DB (PostgreSQL) ===")
    smoke_db()
