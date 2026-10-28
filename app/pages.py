"""HTML-страницы, которые видит человек, открывший адрес сервиса в браузере."""


def render_home(*, books: int | None, authors: int | None, database: str) -> str:
    if books is None or authors is None:
        stats = "Каталог ещё готовится. Обновите страницу через несколько секунд."
    else:
        stats = f"В каталоге {books} {_books(books)} и {authors} {_authors(authors)}."

    return _layout(
        title="Library API",
        body=f"""
        <p class="eyebrow">REST API библиотеки</p>
        <h1>Книги, авторы и выдача</h1>
        <p class="lead">
          Открытый сервис на FastAPI: регистрация читателей, JWT и роли,
          каталог книг и учёт, у кого какой экземпляр на руках.
        </p>
        <p class="stats">{stats} База: {database}.</p>
        <div class="actions">
          <a class="primary" href="/api/docs">Открыть Swagger</a>
          <a href="/books?limit=100">Книги (JSON)</a>
          <a href="/authors?limit=100">Авторы (JSON)</a>
        </div>
        <section>
          <h2>С чего начать</h2>
          <ol>
            <li>Откройте <a href="/api/docs">/api/docs</a> и посмотрите схему запросов.</li>
            <li>Зарегистрируйте читателя: <code>POST /register</code>.</li>
            <li>Каталог читается без токена: <code>GET /books</code> и <code>GET /authors</code>.</li>
          </ol>
          <pre><code>curl https://libraryapi-main.layero.app/api/health
curl https://libraryapi-main.layero.app/books</code></pre>
        </section>
        <p class="note">
          Пути <code>/docs</code>, <code>/redoc</code> и <code>/health</code> на хостинге
          занимает сама платформа. Документация сервиса живёт на
          <a href="/api/docs">/api/docs</a>, проверка живости — на
          <a href="/api/health">/api/health</a>.
        </p>
        """,
    )


def render_not_found(path: str) -> str:
    safe_path = (
        path.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
    return _layout(
        title="Страница не найдена — Library API",
        body=f"""
        <p class="eyebrow">404</p>
        <h1>Такой страницы нет</h1>
        <p class="lead">Адрес <code>{safe_path}</code> никуда не ведёт. Это API, а не набор HTML-страниц.</p>
        <div class="actions">
          <a class="primary" href="/">На главную</a>
          <a href="/api/docs">Swagger</a>
          <a href="/books">Книги</a>
          <a href="/authors">Авторы</a>
        </div>
        """,
    )


def _books(count: int) -> str:
    return _plural(count, "книга", "книги", "книг")


def _authors(count: int) -> str:
    return _plural(count, "автор", "автора", "авторов")


def _plural(count: int, one: str, few: str, many: str) -> str:
    number = abs(count) % 100
    if 11 <= number <= 14:
        return many
    tail = number % 10
    if tail == 1:
        return one
    if 2 <= tail <= 4:
        return few
    return many


def _layout(*, title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #16130f;
      --card: #221c16;
      --ink: #f4efe6;
      --muted: #c3b6a4;
      --line: #3a3128;
      --accent: #e4b15a;
      --accent-ink: #2a1c08;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
      background:
        radial-gradient(1200px 500px at 10% -10%, rgba(228, 177, 90, 0.16), transparent 55%),
        var(--bg);
      color: var(--ink);
    }}
    main {{
      max-width: 740px;
      margin: 0 auto;
      padding: 64px 24px 80px;
    }}
    .eyebrow {{
      margin: 0 0 12px;
      font-family: "Segoe UI", sans-serif;
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--accent);
    }}
    h1 {{
      margin: 0 0 16px;
      font-size: 48px;
      font-weight: 600;
      line-height: 1.05;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 22px;
    }}
    .lead, .stats, .note, li {{
      font-family: "Segoe UI", sans-serif;
      color: var(--muted);
      line-height: 1.55;
    }}
    .lead {{ font-size: 18px; margin: 0 0 12px; }}
    .stats, .note {{ margin: 0 0 28px; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 36px; }}
    a {{
      color: var(--accent);
      font-family: "Segoe UI", sans-serif;
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}
    .actions a {{
      display: inline-block;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--card);
      text-decoration: none;
    }}
    .actions a.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: var(--accent-ink);
      font-weight: 600;
    }}
    section {{
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }}
    ol {{ margin: 0 0 16px; padding-left: 20px; }}
    pre {{
      margin: 0;
      padding: 14px 16px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border-radius: 12px;
      background: #100e0c;
      border: 1px solid var(--line);
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 14px;
    }}
  </style>
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>
"""
