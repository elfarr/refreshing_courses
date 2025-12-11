from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from queue import Empty
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

from adapters import DbRepoAdapter, JsonRepoAdapter, YamlRepoAdapter
from instructor_repo_iface import InstructorRepo
from webapp.add_controller import AddWindowController
from webapp.controller import InstructorController
from webapp.edit_controller import EditWindowController
from webapp.observable_repo import ObservableInstructorRepo
from webapp.views import render_add_page, render_details_page, render_edit_page, render_main_page


def _parse_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    if not raw:
        return {}
    try:
        return cast(dict[str, Any], json.loads(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc


def _send_json(
    handler: BaseHTTPRequestHandler, payload: Any, status: HTTPStatus = HTTPStatus.OK
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _send_text(handler: BaseHTTPRequestHandler, message: str, status: HTTPStatus) -> None:
    body = message.encode("utf-8", errors="ignore")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _write_sse(handler: BaseHTTPRequestHandler, data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False)
    handler.wfile.write(f"data: {payload}\n\n".encode())
    handler.wfile.flush()


def _extract_id(path: str) -> int | None:
    parts = [p for p in path.split("/") if p]
    if not parts:
        return None
    try:
        return int(parts[-1])
    except ValueError:
        return None


def make_handler(
    controller: InstructorController,
    add_controller: AddWindowController,
    edit_controller: EditWindowController,
) -> type[BaseHTTPRequestHandler]:
    class MVCHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                items = controller.list_profiles_payload()
                html = render_main_page(items)
                self._send_html(html)
                return
            if parsed.path == "/details":
                params = parse_qs(parsed.query)
                instructor_id = _parse_int(params.get("id", [None])[0])
                if instructor_id is None:
                    _send_text(self, "Некорректный id", HTTPStatus.BAD_REQUEST)
                    return
                payload = controller.get_instructor_payload(instructor_id)
                html = render_details_page(instructor_id, payload)
                self._send_html(html)
                return
            if parsed.path == "/add":
                html = render_add_page()
                self._send_html(html)
                return
            if parsed.path == "/edit":
                params = parse_qs(parsed.query)
                instructor_id = _parse_int(params.get("id", [None])[0])
                if instructor_id is None:
                    _send_text(self, "Некорректный id", HTTPStatus.BAD_REQUEST)
                    return
                payload = controller.get_instructor_payload(instructor_id)
                html = render_edit_page(instructor_id, payload)
                self._send_html(html)
                return
            if parsed.path.startswith("/api/instructors"):
                self._handle_api_get(parsed.path)
                return
            if parsed.path == "/events":
                self._handle_events(parsed.query)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/add":
                self._handle_add_post()
                return
            if parsed.path != "/api/instructors":
                self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
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
            if parsed.path.startswith("/api/edit/"):
                self._handle_edit_put(parsed.path)
                return
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

        def _handle_api_get(self, path: str) -> None:
            if path == "/api/instructors":
                items = controller.list_profiles_payload()
                payload = {"items": items, "count": controller.count()}
                _send_json(self, payload)
                return
            instructor_id = _extract_id(path)
            if instructor_id is None:
                _send_text(self, "Некорректный ID", HTTPStatus.BAD_REQUEST)
                return
            instructor_payload: dict[str, Any] | None = controller.get_instructor_payload(
                instructor_id
            )
            if instructor_payload is None:
                _send_text(self, "Инструктор не найден", HTTPStatus.NOT_FOUND)
                return
            _send_json(self, instructor_payload)

        def _handle_events(self, query: str) -> None:
            params = parse_qs(query)
            instructor_id = _parse_int(params.get("id", [None])[0])
            queue, unsubscribe = controller.subscribe_to_instructor(instructor_id)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            initial_payload: dict[str, Any]
            if instructor_id is None:
                initial_payload = {
                    "action": "snapshot",
                    "payload": controller.list_profiles_payload(),
                    "instructor_id": None,
                }
            else:
                payload_obj: dict[str, Any] = controller.get_instructor_payload(instructor_id) or {}
                initial_payload = {
                    "action": "snapshot",
                    "payload": payload_obj,
                    "instructor_id": instructor_id,
                }
            _write_sse(self, initial_payload)

            try:
                while True:
                    try:
                        event = queue.get(timeout=15)
                    except Empty:
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
                        continue
                    payload = {
                        "action": event.action,
                        "instructor_id": event.instructor_id,
                        "payload": event.payload,
                    }
                    _write_sse(self, payload)
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                unsubscribe()

        def _handle_add_post(self) -> None:
            try:
                payload = _read_json(self)
                result = add_controller.create_instructor(payload)
            except Exception as exc:  # noqa: BLE001
                _send_text(self, str(exc), HTTPStatus.BAD_REQUEST)
                return
            _send_json(self, result, HTTPStatus.CREATED)

        def _handle_edit_put(self, path: str) -> None:
            instructor_id = _extract_id(path)
            if instructor_id is None:
                self.send_error(HTTPStatus.BAD_REQUEST, "ID required")
                return
            try:
                payload = _read_json(self)
                result = edit_controller.update_instructor(instructor_id, payload)
            except Exception as exc:  # noqa: BLE001
                _send_text(self, str(exc), HTTPStatus.BAD_REQUEST)
                return
            _send_json(self, result)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
            return

    return MVCHandler


def build_controller(
    storage: str,
    *,
    kind: str = "yaml",
    db_params: dict[str, Any] | None = None,
) -> InstructorController:
    base_repo: InstructorRepo
    if kind == "json":
        base_repo = JsonRepoAdapter(storage)
    elif kind == "yaml":
        base_repo = YamlRepoAdapter(storage)
    elif kind == "db":
        if not db_params:
            raise ValueError()
        base_repo = DbRepoAdapter(**db_params)
    else:
        raise ValueError()
    observable = ObservableInstructorRepo(base_repo)
    return InstructorController(observable)


def serve(
    controller: InstructorController,
    add_controller: AddWindowController,
    edit_controller: EditWindowController,
    host: str = "127.0.0.1",
    port: int = 8080,
) -> None:
    handler = make_handler(controller, add_controller, edit_controller)
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
    parser = argparse.ArgumentParser(description="Простое MVC веб-приложение без фреймворка")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--storage", default="instructors.yaml", help="Path to JSON/YAML file")
    parser.add_argument(
        "--format", default="yaml", choices=["yaml", "json", "db"], help="Storage type"
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
    add_controller = AddWindowController(controller)
    edit_controller = EditWindowController(controller)
    serve(controller, add_controller, edit_controller, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
