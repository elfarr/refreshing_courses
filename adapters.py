from __future__ import annotations
from typing import List
from Instructor import Instructor
from PublicInstructorProfile import PublicInstructorProfile
from instructor_repo_iface import InstructorRepo

from Instructor_rep_json import InstructorRepJson
from Instructor_rep_yaml import InstructorRepYaml
from Instructor_rep_db import InstructorRepDB
from db_singleton import PostgresDB 

class JsonRepoAdapter(InstructorRepo):
    def __init__(self, path: str):
        self._adaptee = InstructorRepJson(path)

    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._adaptee.get_by_id(instructor_id)

    def get_k_n_short_list(self, k: int, n: int) -> List[PublicInstructorProfile]:
        return self._adaptee.get_k_n_short_list(k, n)

    def add(self, item: Instructor) -> Instructor:
        return self._adaptee.add(item)

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        return self._adaptee.replace_by_id(instructor_id, new_item)

    def delete_by_id(self, instructor_id: int) -> bool:
        return self._adaptee.delete_by_id(instructor_id)

    def get_count(self) -> int:
        return self._adaptee.get_count()


class YamlRepoAdapter(InstructorRepo):
    def __init__(self, path: str):
        self._adaptee = InstructorRepYaml(path)

    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._adaptee.get_by_id(instructor_id)

    def get_k_n_short_list(self, k: int, n: int) -> List[PublicInstructorProfile]:
        return self._adaptee.get_k_n_short_list(k, n)

    def add(self, item: Instructor) -> Instructor:
        return self._adaptee.add(item)

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        return self._adaptee.replace_by_id(instructor_id, new_item)

    def delete_by_id(self, instructor_id: int) -> bool:
        return self._adaptee.delete_by_id(instructor_id)

    def get_count(self) -> int:
        return self._adaptee.get_count()


class DbRepoAdapter(InstructorRepo):
    def __init__(self, *, host: str, port: int, dbname: str, user: str, password: str):
        db = PostgresDB(host=host, port=port, dbname=dbname, user=user, password=password)
        self._adaptee = InstructorRepDB(db)

    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._adaptee.get_by_id(instructor_id)

    def get_k_n_short_list(self, k: int, n: int) -> List[PublicInstructorProfile]:
        return self._adaptee.get_k_n_short_list(k, n)

    def add(self, item: Instructor) -> Instructor:
        return self._adaptee.add(item)

    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        return self._adaptee.replace_by_id(instructor_id, new_item)

    def delete_by_id(self, instructor_id: int) -> bool:
        return self._adaptee.delete_by_id(instructor_id)

    def get_count(self) -> int:
        return self._adaptee.get_count()
