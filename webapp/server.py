from __future__ import annotations

# парсинг аргументов командной строки
import argparse
from http import HTTPStatus

# базовый обработчик http запросов и http сервер
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from queue import Empty
from typing import Any, cast

# разбор url и query
from urllib.parse import ParseResult, parse_qs, urlparse

# мои адаптеры
from adapters import DbRepoAdapter, JsonRepoAdapter, YamlRepoAdapter
from instructor_repo_iface import InstructorRepo
from webapp.controller import InstructorController
from webapp.observable_repo import ObservableInstructorRepo
from webapp.views import render_details_page, render_main_page


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# чтение json тела из запроса
def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    data = handler.rfile.read(length).decode("utf-8") if length else "{}"
    if not data:
        return {}
    try:
        return cast(dict[str, Any], json.loads(data))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Некорректный JSON: {exc}") from exc


# отправляет json
def _send_json(
    handler: BaseHTTPRequestHandler, payload: Any, status: HTTPStatus = HTTPStatus.OK
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


# отправляет текстовый ответ
def _send_text(handler: BaseHTTPRequestHandler, message: str, status: HTTPStatus) -> None:
    body = message.encode("utf-8", errors="ignore")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


# создание события
def _write_sse(handler: BaseHTTPRequestHandler, data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False)
    handler.wfile.write(f"data: {payload}\n\n".encode())
    # "заталкиваем" данные в браузер
    handler.wfile.flush()


# достаем id из пути
def _extract_id(path: str) -> int | None:
    parts = [p for p in path.split("/") if p]
    if not parts:
        return None
    try:
        return int(parts[-1])
    except ValueError:
        return None


# http обработчик
def make_handler(controller: InstructorController) -> type[BaseHTTPRequestHandler]:
    ## фабрика классов - создает класс обработчик http запросов, в котором внутри нужный контроллер
    # делаем так, потому что нам нужно передать именно КЛАСС в функцию ThreadingHTTPServer

    class MVCHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)

            if parsed.path == "/":
                ## получаем json с инструкторами
                items = controller.list_profiles_payload()
                html = render_main_page(items)
                self._send_html(html)
                return

            if parsed.path == "/details":
                # парсим параметры из ссылки
                params = parse_qs(parsed.query)
                raw_id = params.get("id", [None])[0]
                instructor_id = _parse_int(raw_id)
                if instructor_id is None:
                    _send_text(self, "Некорректный id", HTTPStatus.BAD_REQUEST)
                    return

                payload = controller.get_instructor_payload(instructor_id)
                html = render_details_page(instructor_id, payload)
                self._send_html(html)
                return

            if parsed.path.startswith("/api/instructors"):
                self._handle_api_get(parsed)
                return

            if parsed.path.startswith("/events"):
                self._handle_events(parsed)
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/api/instructors":
                self.send_error(HTTPStatus.NOT_FOUND, "Route not supported")
                return
            try:
                payload = _read_json(self)
                result = controller.create_instructor(payload)
            except Exception as exc:  # noqa: BLE001
                _send_text(self, str(exc), HTTPStatus.BAD_REQUEST)
                return
            _send_json(self, result, HTTPStatus.CREATED)

        def do_PUT(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            instructor_id = _extract_id(parsed.path)
            if instructor_id is None:
                self.send_error(HTTPStatus.BAD_REQUEST, "ID required")
                return
            try:
                payload = _read_json(self)
                result = controller.update_instructor(instructor_id, payload)
            except Exception as exc:  # noqa: BLE001
                _send_text(self, str(exc), HTTPStatus.BAD_REQUEST)
                return
            _send_json(self, result)

        def do_DELETE(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            instructor_id = _extract_id(parsed.path)
            if instructor_id is None:
                self.send_error(HTTPStatus.BAD_REQUEST, "ID required")
                return
            deleted = controller.delete_instructor(instructor_id)
            if not deleted:
                _send_text(self, "Инструктор не найден", HTTPStatus.NOT_FOUND)
                return
            _send_json(self, {"status": "deleted", "instructor_id": instructor_id})

        # эндпоинты для апишек
        def _handle_api_get(self, parsed: ParseResult) -> None:
            if parsed.path == "/api/instructors":
                items = controller.list_profiles_payload()
                list_payload = {"items": items, "count": controller.count()}
                _send_json(self, list_payload)
                return
            instructor_id = _extract_id(parsed.path)
            if instructor_id is None:
                _send_text(self, "Неверный ID", HTTPStatus.BAD_REQUEST)
                return
            instructor_payload = controller.get_instructor_payload(instructor_id)
            if instructor_payload is None:
                _send_text(self, "Инструктор не найден", HTTPStatus.NOT_FOUND)
                return
            _send_json(self, instructor_payload)

        # обработчик sse соединения
        def _handle_events(self, parsed: ParseResult) -> None:
            params = parse_qs(parsed.query)
            raw_id = params.get("id", [None])[0]
            instructor_id = _parse_int(raw_id)
            # в очередь приходят все события по конкретному инструктору (это массив из объектов)
            # unsubscribe - функция, которую нужно вызвать, когда клиент отключится, чтобы удалить эту очередь из списка подписчиков
            queue, unsubscribe = controller.subscribe_to_instructor(instructor_id)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            # не кэшируем чтобы всегда было актуальное соединение
            self.send_header("Cache-Control", "no-cache")
            # держим соединение открытым
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            # начальное состояние берем
            initial_payload: Any
            # если нет конктерного инструтора, то берем информацию о всех
            if instructor_id is None:
                # снепшот - снимок текущего состояния
                initial_payload = {
                    "action": "snapshot",
                    "payload": controller.list_profiles_payload(),
                    "instructor_id": None,
                }
            else:
                initial_payload = {
                    "action": "snapshot",
                    "payload": controller.get_instructor_payload(instructor_id),
                    "instructor_id": instructor_id,
                }
            _write_sse(self, initial_payload)

            try:
                while True:
                    try:
                        # принимаем из очереди (ждем 15 сек)
                        event = queue.get(timeout=15)
                    # если никто ничего не изменил за 15 секунд то оставляем соединение включенным
                    except Empty:
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
                        continue
                    # если что-то получили из очереди
                    payload = {
                        "action": event.action,
                        "instructor_id": event.instructor_id,
                        "payload": event.payload,
                    }
                    # отсылаем браузеру
                    _write_sse(self, payload)
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                unsubscribe()

        # отправление hmtl в браузер
        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            # wfile - поток, завязанный на сокет соединения с клиентом
            self.wfile.write(body)

    return MVCHandler


# выбираем контроллер в зависимости от аргументов
def build_controller(
    storage: str,
    *,
    kind: str = "json",
    db_params: dict[str, Any] | None = None,
) -> InstructorController:
    base_repo: InstructorRepo
    if kind == "json":
        base_repo = JsonRepoAdapter(storage)
    elif kind == "yaml":
        base_repo = YamlRepoAdapter(storage)
    elif kind == "db":
        if not db_params:
            raise ValueError("Должны быть указаны параметры для подключения в БД")
        base_repo = DbRepoAdapter(**db_params)
    else:
        raise ValueError(f"Недопустимый тип хранилища: {kind}")
    observable = ObservableInstructorRepo(base_repo)
    return InstructorController(observable)


def serve(controller: InstructorController, host: str = "127.0.0.1", port: int = 8080) -> None:
    # передали наш обработчик
    handler = make_handler(controller)
    # создаем сервер по указанному порту хосту и с обработчиком
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Веб-сервер запущен: http://{host}:{port}")
    print("Ctrl+C для остановки. Главная страница: /")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="MVC приложение")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument(
        "--storage", default="instructors.yaml", help="Путь к JSON/YAML файлу или имя БД"
    )
    parser.add_argument(
        "--format",
        default="yaml",
        choices=["yaml", "json", "db"],
        help="Тип хранилища: yaml/json/db",
    )
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", default=5432, type=int)
    parser.add_argument("--db-name", default="postgres")
    parser.add_argument("--db-user", default="postgres")
    parser.add_argument("--db-password", default="1234")
    args = parser.parse_args()

    db_params = {
        "host": args.db_host,
        "port": args.db_port,
        "dbname": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
    }

    controller = build_controller(
        args.storage,
        kind=args.format,
        db_params=db_params if args.format == "db" else None,
    )
    serve(controller, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
