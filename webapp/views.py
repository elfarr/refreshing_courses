from __future__ import annotations

from html import escape
import json
from typing import Any


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def render_main_page(items: list[dict[str, Any]]) -> str:
    # данные обо всех инструкторах
    data_json = _json(items)
    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\" />
  <title>Преподаватели — MVC CRUD</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f3f4f6; color: #111; }}
    header {{ background: #1f2937; color: #fff; padding: 1rem 2rem; }}
    main {{ padding: 1.5rem 2rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; background: #fff; }}
    th, td {{ padding: 0.5rem 0.75rem; border-bottom: 1px solid #e5e7eb; text-align: left; }}
    th {{ background: #f9fafb; font-weight: 600; }}
    tbody tr:hover {{ background: #f3f4f6; }}
    .actions button {{ margin-right: 0.4rem; }}
    form {{ background: #fff; padding: 1rem; border-radius: 0.25rem; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
    label {{ display: block; margin-top: 0.5rem; font-size: 0.9rem; color: #374151; }}
    input {{ width: 100%; padding: 0.45rem; margin-top: 0.2rem; border: 1px solid #d1d5db; border-radius: 0.25rem; }}
    button {{ padding: 0.4rem 0.8rem; border: none; border-radius: 0.25rem; background: #2563eb; color: #fff; cursor: pointer; }}
    button.secondary {{ background: #6b7280; }}
  </style>
</head>
<body>
  <header>
    <h1>Преподавательский состав курсов повышения квалификации</h1>
    <p>Кликните “Подробнее” чтобы открыть отдельную вкладку с полной информацией и live-обновлениями.</p>
  </header>
  <main>
    <section>
      <div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;\">
        <h2 style=\"margin:0\">Текущие данные</h2>
        <button id=\"refresh-btn\" class=\"secondary\">Обновить таблицу</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Фамилия</th>
            <th>Имя</th>
            <th>Опыт</th>
            <th>Контакты</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody id=\"instructors-body\"></tbody>
      </table>
    </section>
    <section>
      <h2>Форма создания / редактирования</h2>
      <form id=\"instructor-form\" data-mode=\"create\">
        <input type=\"hidden\" name=\"instructor_id\" />
        <label>Фамилия<input required name=\"last_name\" /></label>
        <label>Имя<input required name=\"first_name\" /></label>
        <label>Отчество<input name=\"patronymic\" /></label>
        <label>Телефон<input required name=\"phone\" /></label>
        <label>Опыт, лет<input required type=\"number\" min=\"0\" max=\"80\" name=\"experience_years\" /></label>
        <div style=\"margin-top:0.75rem;\">
          <button type=\"submit\">Сохранить</button>
          <button type=\"button\" id=\"reset-btn\" class=\"secondary\">Очистить форму</button>
        </div>
      </form>
    </section>
  </main>
  <script>
    const tableBody = document.getElementById('instructors-body');
    const refreshBtn = document.getElementById('refresh-btn');
    const form = document.getElementById('instructor-form');
    const resetBtn = document.getElementById('reset-btn');
    let cache = {{ data: {{ items: {data_json} }} }};

    function renderTable(items) {{
      const rows = items.map(item => `
        <tr>
          <td>${{item.instructor_id}}</td>
          <td>${{item.last_name}}</td>
          <td>${{item.first_name}}</td>
          <td>${{item.experience_years}}</td>
          <td>${{item.contact}}</td>
          <td class=\"actions\">
            <button type=\"button\" onclick=\"openDetails(${{item.instructor_id}})\">Подробнее</button>
            <button type=\"button\" onclick=\"fillForm(${{item.instructor_id}})\">Редактировать</button>
            <button type=\"button\" onclick=\"deleteInstructor(${{item.instructor_id}})\">Удалить</button>
          </td>
        </tr>`).join('');
      tableBody.innerHTML = rows || '<tr><td colspan=\"6\">Нет данных</td></tr>';
    }}

    function openDetails(id) {{
      window.open(`/details?id=${{id}}`, '_blank');
    }}

    function fillForm(id) {{
      const item = cache.data.items.find(x => x.instructor_id === id);
      if (!item) return;
      form.dataset.mode = 'edit';
      form.instructor_id.value = item.instructor_id;
      form.last_name.value = item.last_name;
      form.first_name.value = item.first_name;
      form.patronymic.value = item.patronymic || '';
      form.phone.value = item.phone;
      form.experience_years.value = item.experience_years;
    }}

    async function deleteInstructor(id) {{
      if (!confirm('Удалить инструктора #' + id + '?')) return;
      await fetch(`/api/instructors/${{id}}`, {{ method: 'DELETE' }});
      await refresh();
    }}

    async function refresh() {{
      const res = await fetch('/api/instructors');
      if (!res.ok) return;
      const data = await res.json();
      cache.data = data;
      renderTable(data.items);
    }}

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      payload.experience_years = Number(payload.experience_years);
      const mode = form.dataset.mode;
      const targetId = payload.instructor_id;
      const url = mode === 'edit' && targetId ? `/api/instructors/${{targetId}}` : '/api/instructors';
      const method = mode === 'edit' ? 'PUT' : 'POST';
      if (mode !== 'edit') delete payload.instructor_id;
      const res = await fetch(url, {{
        method,
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload)
      }});
      if (res.ok) {{
        form.reset();
        form.dataset.mode = 'create';
        await refresh();
      }} else {{
        alert('Ошибка: ' + await res.text());
      }}
    }});

    resetBtn.addEventListener('click', () => {{
      form.reset();
      form.dataset.mode = 'create';
    }});

    refreshBtn.addEventListener('click', refresh);

    renderTable(cache.data.items);

    const source = new EventSource('/events');
    source.onmessage = () => refresh();
  </script>
</body>
</html>"""


def render_details_page(instructor_id: int, payload: dict[str, Any] | None) -> str:
    payload_json = _json(payload or {})
    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\" />
  <title>Инструктор #{escape(str(instructor_id))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #111; }}
    .card {{ border: 1px solid #e5e7eb; padding: 1rem 1.5rem; border-radius: 0.35rem; max-width: 520px; }}
    h1 {{ margin-top: 0; }}
    dt {{ font-weight: 600; margin-top: 0.3rem; }}
    dd {{ margin-left: 0; margin-bottom: 0.5rem; }}
    .status {{ margin-top: 1rem; color: #047857; font-weight: 600; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>Инструктор #{escape(str(instructor_id))}</h1>
    <p id=\"status\">Live-обновление включено (Observer > SSE)</p>
    <dl>
      <dt>ФИО</dt><dd id=\"fio\"></dd>
      <dt>Телефон</dt><dd id=\"phone\"></dd>
      <dt>Опыт</dt><dd id=\"exp\"></dd>
    </dl>
  </div>
  <script>
    const TARGET_ID = {instructor_id};
    const INITIAL = {payload_json};

    function render(item) {{
      if (!item || !item.instructor_id) {{
        document.getElementById('status').textContent = 'Инструктор удален или отсутствует';
        document.getElementById('fio').textContent = '—';
        document.getElementById('phone').textContent = '—';
        document.getElementById('exp').textContent = '—';
        return;
      }}
      document.getElementById('fio').textContent = `${{item.last_name}} ${{item.first_name}} ${{item.patronymic || ''}}`;
      document.getElementById('phone').textContent = item.phone;
      document.getElementById('exp').textContent = item.experience_years + ' лет';
    }}

    render(INITIAL);

    const source = new EventSource(`/events?id=${{TARGET_ID}}`);
    source.onmessage = (event) => {{
      if (!event.data) return;
      const payload = JSON.parse(event.data);
      render(payload.payload);
    }};
  </script>
</body>
</html>"""


__all__ = ["render_main_page", "render_details_page"]
