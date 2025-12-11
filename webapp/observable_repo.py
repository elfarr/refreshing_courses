from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from queue import Queue
from threading import Lock
from typing import Any

from Instructor import Instructor
from instructor_repo_iface import InstructorRepo
from PublicInstructorProfile import PublicInstructorProfile
from webapp.serializers import as_public_dict


# объект нельзя менять, чтобы он корректно передавался через потоки
# датакласс чтобы не писать инит
@dataclass(frozen=True)
class RepoEvent:
    action: str
    # к какому именно объекту относится событие
    instructor_id: int | None
    # словарь с данными об объекте
    payload: dict[str, Any] | None


# декоратор над базовым интерфейсом репозитория, добавляется подписки на изменения
class ObservableInstructorRepo(InstructorRepo):
    def __init__(self, base: InstructorRepo):
        self._base = base
        self._lock = Lock()
        # подписчики на события. ключ - айди объекта или пусто если все объекты, значение - очередь событий
        self._observers: dict[int | None, list[Queue[RepoEvent]]] = {}

    def subscribe(
        self, instructor_id: int | None = None
    ) -> tuple[Queue[RepoEvent], Callable[[], None]]:
        # создаем новую очередь
        q: Queue[RepoEvent] = Queue()
        # Одновременно только один поток может менять словарь
        with self._lock:
            # добавляем к пустому или существующему полю эту очередь
            self._observers.setdefault(instructor_id, []).append(q)

        # внутренняя функция чтобы нигде не запомнать id очереди созданной
        def unsubscribe() -> None:
            with self._lock:
                # достаем список очередей у объекта
                observers = self._observers.get(instructor_id)
                if not observers:
                    return
                try:
                    # из списка очередей у объекта удаляем нашу очередь
                    observers.remove(q)
                except ValueError:
                    return
                # если это была единственная очередь то в принцие все подписки на этот объект удаляем
                if not observers:
                    self._observers.pop(instructor_id, None)

        return q, unsubscribe

    # получение тех, кому отправлять событие
    def _iter_targets(self, instructor_id: int | None) -> Iterable[Queue[RepoEvent]]:
        with self._lock:
            # подписка на конкретные объекты
            specific = list(self._observers.get(instructor_id, ()))
            # подписка на всех сразу
            broadcast = list(self._observers.get(None, ()))
        return [*broadcast, *specific]

    # рассылка уведомлений по событиям подписчикам (нужным очередям)
    def _notify(
        self,
        action: str,
        entity: Instructor | PublicInstructorProfile | None,
        *,
        subject_id: int | None = None,
    ) -> None:
        payload = as_public_dict(entity)
        event = RepoEvent(
            action=action,
            instructor_id=subject_id or (payload or {}).get("instructor_id"),
            payload=payload,
        )
        for queue in self._iter_targets(event.instructor_id):
            queue.put(event)

    def get_by_id(self, instructor_id: int) -> Instructor | None:
        return self._base.get_by_id(instructor_id)

    def get_k_n_short_list(self, k: int, n: int) -> list[PublicInstructorProfile]:
        return self._base.get_k_n_short_list(k, n)

    # когда мы добавляем объект в репозиторий, еще создается уведомление
    def add(self, item: Instructor) -> Instructor:
        created = self._base.add(item)
        self._notify("created", PublicInstructorProfile(created))
        return created

    # когда обновляется
    def replace_by_id(self, instructor_id: int, new_item: Instructor) -> bool:
        if not self._base.replace_by_id(instructor_id, new_item):
            return False
        updated = self._base.get_by_id(instructor_id)
        if updated:
            self._notify("updated", PublicInstructorProfile(updated))
        return True

    def delete_by_id(self, instructor_id: int) -> bool:
        deleted = self._base.delete_by_id(instructor_id)
        if deleted:
            self._notify("deleted", None, subject_id=instructor_id)
        return deleted

    def get_count(self) -> int:
        return self._base.get_count()

    def sort_by_last_name(self, reverse: bool = False) -> list[Instructor]:
        sorted_items = self._base.sort_by_last_name(reverse)
        for queue in self._iter_targets(None):
            queue.put(RepoEvent(action="sorted", instructor_id=None, payload=None))
        return sorted_items


__all__ = ["ObservableInstructorRepo", "RepoEvent"]
