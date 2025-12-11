from __future__ import annotations

from html import escape
import json
from typing import Any


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def render_main_page(items: list[dict[str, Any]]) -> str:
    data_json = _json(items)
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Инструкторы — MVC CRUD</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --card: #ffffff;
      --accent: #2563eb;
      --accent-2: #111827;
      --text: #0f172a;
      --muted: #6b7280;
      --border: #e5e7eb;
      --shadow: 0 14px 38px rgba(15,23,42,0.08);
      --radius: 12px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: "Inter","Segoe UI",system-ui,sans-serif; margin: 0; background: linear-gradient(135deg,#f8fafc 0%,#eef2ff 100%); color: var(--text); }}
    header {{ background: var(--card); padding: 1.2rem 2rem; box-shadow: var(--shadow); position: sticky; top: 0; z-index: 10; }}
    header h1 {{ margin: 0 0 0.35rem 0; font-size: 1.3rem; }}
    header p {{ margin: 0; color: var(--muted); }}
    main {{ padding: 1.5rem 2rem; max-width: 1200px; margin: 0 auto; }}
    .card {{ background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 1.25rem; margin-bottom: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); text-align: left; }}
    th {{ background: #f8fafc; font-weight: 600; }}
    tbody tr:hover {{ background: #f1f5f9; }}
    .actions button {{ margin-right: 0.35rem; }}
    button {{ padding: 0.5rem 0.95rem; border: none; border-radius: 8px; background: var(--accent); color: #fff; cursor: pointer; font-weight: 600; }}
    button.secondary {{ background: var(--muted); color: #fff; }}
    #add-window-btn {{ margin-top: 0.5rem; background: var(--accent-2); }}
  </style>
</head>
<body>
  <header>
    <h1>Инструкторы</h1>
    <button id="add-window-btn">Добавить в новом окне</button>
  </header>
  <main>
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:0.75rem;">
        <div style="flex:1;">
          <h2 style="margin:0 0 0.25rem 0;">Текущие данные</h2>
          <p style="margin:0;color:var(--muted);">Двойной клик по строке - открыть детали</p>
          <form id="filter-form" style="margin-top:0.5rem;display:flex;flex-wrap:wrap;gap:0.5rem;">
            <input name="last_name" placeholder="Фамилия содержит" style="flex:1;min-width:140px;padding:0.45rem;border:1px solid var(--border);border-radius:8px;" />
            <input name="first_name" placeholder="Имя содержит" style="flex:1;min-width:140px;padding:0.45rem;border:1px solid var(--border);border-radius:8px;" />
            <input name="min_exp" type="number" min="0" max="80" placeholder="Мин. опыт" style="width:120px;padding:0.45rem;border:1px solid var(--border);border-radius:8px;" />
            <input name="max_exp" type="number" min="0" max="80" placeholder="Макс. опыт" style="width:120px;padding:0.45rem;border:1px solid var(--border);border-radius:8px;" />
            <select name="order_by" style="width:180px;padding:0.45rem;border:1px solid var(--border);border-radius:8px;">
              <option value="">Сортировка: по фамилии</option>
              <option value="last_name asc">Фамилия ↑</option>
              <option value="last_name desc">Фамилия ↓</option>
              <option value="experience_years asc">Опыт ↑</option>
              <option value="experience_years desc">Опыт ↓</option>
            </select>
            <button type="submit" class="secondary" style="padding:0.45rem 0.9rem;">Фильтр</button>
            <button type="button" id="clear-filter" class="secondary" style="padding:0.45rem 0.9rem;background:#9ca3af;">Сброс</button>
          </form>
        </div>
        <button id="refresh-btn" class="secondary">Обновить таблицу</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Отображаемое имя</th>
            <th>Опыт</th>
            <th>Контакт</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody id="instructors-body"></tbody>
      </table>
    </div>
  </main>
  <script>
    const tableBody = document.getElementById('instructors-body');
    const refreshBtn = document.getElementById('refresh-btn');
    const addWindowBtn = document.getElementById('add-window-btn');
    const filterForm = document.getElementById('filter-form');
    const clearFilterBtn = document.getElementById('clear-filter');
    let cache = {{ data: {{ items: {data_json} }} }};

    function renderTable(items) {{
      const rows = items.map(item => `
        <tr>
          <td>${{item.instructor_id}}</td>
          <td>${{item.display_name || item.last_name || ''}}</td>
          <td>${{item.experience_years}} лет</td>
          <td>${{item.contact}}</td>
          <td class="actions">
            <button type="button" onclick="openDetails(${{item.instructor_id}})">Подробнее</button>
            <button type="button" onclick="openEdit(${{item.instructor_id}})">Редактировать</button>
            <button type="button" onclick="deleteInstructor(${{item.instructor_id}})">Удалить</button>
          </td>
        </tr>`).join('');
      tableBody.innerHTML = rows || '<tr><td colspan="5">Нет данных</td></tr>';
    }}

    tableBody.addEventListener('dblclick', (e) => {{
      const row = e.target.closest('tr');
      if (!row) return;
      const idCell = row.querySelector('td');
      const id = Number(idCell?.textContent);
      if (id) openDetails(id);
    }});

    function openDetails(id) {{
      window.open(`/details?id=${{id}}`, '_blank');
    }}

    function openEdit(id) {{
      window.open(`/edit?id=${{id}}`, 'edit_window_' + id, 'width=520,height=720');
    }}

    async function deleteInstructor(id) {{
      if (!confirm('Удалить инструктора #' + id + '?')) return;
      await fetch(`/api/instructors/${{id}}`, {{ method: 'DELETE' }});
      await refresh();
    }}

    function buildQuery() {{
      const formData = new FormData(filterForm);
      const params = new URLSearchParams();
      for (const [key, value] of formData.entries()) {{
        const v = value === null ? '' : String(value).trim();
        if (v !== '') {{
          params.append(key, v);
        }}
      }}
      const qs = params.toString();
      return qs ? `?${{qs}}` : '';
    }}

    async function refresh() {{
      const res = await fetch('/api/instructors' + buildQuery());
      if (!res.ok) return;
      const data = await res.json();
      cache.data = data;
      renderTable(data.items);
    }}

    refreshBtn.addEventListener('click', refresh);
    filterForm.addEventListener('submit', (e) => {{
      e.preventDefault();
      refresh();
    }});
    clearFilterBtn.addEventListener('click', () => {{
      filterForm.reset();
      refresh();
    }});

    addWindowBtn.addEventListener('click', () => {{
      window.open('/add', 'add_window', 'width=520,height=720');
    }});

    window.addEventListener('message', (event) => {{
      if (event.data && event.data.type === 'refresh-table') {{
        refresh();
      }}
    }});

    renderTable(cache.data.items);

    const source = new EventSource('/events');
    source.onmessage = () => refresh();
  </script>
</body>
</html>"""


def render_details_page(instructor_id: int, payload: dict[str, Any] | None) -> str:
    payload_json = _json(payload or {})
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Инструктор #{escape(str(instructor_id))}</title>
  <style>
    :root {{
      --border: #e5e7eb;
      --shadow: 0 14px 38px rgba(15,23,42,0.08);
    }}
    body {{ font-family: "Inter","Segoe UI",system-ui,sans-serif; margin: 2rem; color: #0f172a; background: #f8fafc; }}
    .card {{ border: 1px solid var(--border); padding: 1rem 1.5rem; border-radius: 12px; max-width: 520px; box-shadow: var(--shadow); background: #fff; }}
    h1 {{ margin-top: 0; }}
    dt {{ font-weight: 600; margin-top: 0.3rem; }}
    dd {{ margin-left: 0; margin-bottom: 0.5rem; }}
    .status {{ margin-top: 1rem; color: #047857; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Инструктор #{escape(str(instructor_id))}</h1>
    <p id="status">Live-обновление включено (Observer > SSE)</p>
    <dl>
      <dt>ФИО</dt><dd id="fio"></dd>
      <dt>Телефон</dt><dd id="phone"></dd>
      <dt>Опыт</dt><dd id="exp"></dd>
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


class FormWindow:
    """Единый класс окна (форма add/edit), конфиг передают контроллеры."""

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def render(self) -> str:
        config_json = _json(self.config)
        action = escape(self.config.get("action", "/api/add"))
        method = escape(self.config.get("method", "POST"))
        title = escape(self.config.get("title", "Форма"))
        subtitle = escape(
            self.config.get(
                "subtitle",
                "Заполните поля и отправьте форму. Данные сохранятся и обновят главную таблицу.",
            )
        )
        submit_text = escape(self.config.get("submit_text", "Сохранить"))
        return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    :root {{
      --bg1: #f4f5fb;
      --card: #ffffff;
      --border: #e5e7eb;
      --accent: linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);
      --muted: #6b7280;
      --shadow: 0 18px 40px rgba(15,23,42,0.12);
    }}
    body {{ font-family: "Inter","Segoe UI",system-ui,sans-serif; margin: 0; color: #0f172a;
           background: radial-gradient(circle at 20% 20%, #eef2ff, #f8fafc 35%), var(--bg1); }}
    .wrap {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 1.5rem; }}
    form {{ width: min(520px, 100%); background: var(--card); padding: 1.3rem 1.5rem;
           border-radius: 16px; box-shadow: var(--shadow); border: 1px solid #eef2ff; }}
    h1 {{ margin: 0 0 0.75rem 0; font-size: 1.25rem; }}
    p.lead {{ margin: 0 0 1rem 0; color: var(--muted); }}
    label {{ display: block; margin-top: 0.65rem; font-size: 0.95rem; color: var(--muted); }}
    input {{ width: 100%; padding: 0.6rem; margin-top: 0.25rem; border: 1px solid var(--border); border-radius: 10px; }}
    button {{ width: 100%; padding: 0.65rem 0.9rem; border: none; border-radius: 10px; background: var(--accent);
             color: #fff; cursor: pointer; margin-top: 1rem; font-weight: 700; letter-spacing: 0.01em; }}
  </style>
</head>
<body>
  <div class="wrap">
    <form id="form-window">
      <h1>{title}</h1>
      <p class="lead">{subtitle}</p>
      <label>Фамилия<input required name="last_name" /></label>
      <label>Имя<input required name="first_name" /></label>
      <label>Отчество<input name="patronymic" /></label>
      <label>Телефон<input required name="phone" /></label>
      <label>Опыт, лет<input required type="number" min="0" max="80" name="experience_years" /></label>
      <button type="submit">{submit_text}</button>
    </form>
  </div>
  <script>
    const CONFIG = {config_json};
    const form = document.getElementById('form-window');

    function fill(data) {{
      if (!data) return;
      form.last_name.value = data.last_name || '';
      form.first_name.value = data.first_name || '';
      form.patronymic.value = data.patronymic || '';
      form.phone.value = data.phone || '';
      form.experience_years.value = data.experience_years ?? '';
    }}
    fill(CONFIG.payload);

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      const body = Object.fromEntries(new FormData(form).entries());
      body.experience_years = Number(body.experience_years);
      const res = await fetch(CONFIG.action || "{action}", {{
        method: CONFIG.method || "{method}",
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(body)
      }});
      if (res.ok) {{
        if (window.opener) {{
          window.opener.postMessage({{ type: 'refresh-table' }}, '*');
        }}
        window.close();
      }} else {{
        alert('Ошибка: ' + await res.text());
      }}
    }});
  </script>
</body>
</html>"""


def render_form_page(config: dict[str, Any]) -> str:
    """Хелпер для обратной совместимости."""
    return FormWindow(config).render()


__all__ = ["render_main_page", "render_details_page", "FormWindow", "render_form_page"]
