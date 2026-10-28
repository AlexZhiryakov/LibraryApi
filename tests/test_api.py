"""Тесты API: регистрация/вход, авторизация, CRUD книг и выдача/возврат."""


def _book_by_id(client, book_id):
    books = client.get("/books").json()
    return next(book for book in books if book["id"] == book_id)


def test_health(client):
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_docs_moved_under_api_prefix(client):
    """Swagger и OpenAPI живут под /api — корневые пути перехватывает Layero."""
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/redoc").status_code == 200
    assert client.get("/api/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 404


def test_root_is_a_home_page(client):
    """Корень — страница сервиса, а не редирект: хостинг считает ответ живым только при 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "/api/docs" in response.text
    assert "Книги" in response.text


def test_unknown_html_path_explains_where_docs_are(client):
    response = client.get("/docs", headers={"Accept": "text/html"})
    assert response.status_code == 404
    assert "/api/docs" in response.text
    assert response.headers["content-type"].startswith("text/html")


def test_register_returns_token(client):
    response = client.post("/register", json={"username": "alice", "password": "alice-pass-123"})
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"


def test_register_rejects_short_password(client):
    response = client.post("/register", json={"username": "bob", "password": "short"})
    assert response.status_code == 422


def test_register_ignores_is_admin_field(client):
    """Даже если клиент передаёт is_admin, создаётся обычный пользователь."""
    response = client.post(
        "/register",
        json={"username": "sneaky", "password": "sneaky-pass-123", "is_admin": True},
    )
    assert response.status_code == 201
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    forbidden = client.post("/books", json={"title": "Книга", "genre": "Проза"}, headers=headers)
    assert forbidden.status_code == 403


def test_register_duplicate_username_conflict(client):
    payload = {"username": "dup", "password": "dup-pass-1234"}
    assert client.post("/register", json=payload).status_code == 201
    assert client.post("/register", json=payload).status_code == 409


def test_login_with_wrong_password(client):
    client.post("/register", json={"username": "carol", "password": "carol-pass-123"})
    response = client.post("/token", json={"username": "carol", "password": "wrong-password"})
    assert response.status_code == 401


def test_protected_endpoints_require_token(client):
    assert client.post("/books", json={"title": "X", "genre": "Y"}).status_code == 401
    assert client.get("/users").status_code == 401
    assert client.get("/borrows").status_code == 401


def test_only_admin_can_create_author_and_book(client, admin_headers, reader_headers):
    assert client.post("/authors", json={"name": "Иван"}, headers=reader_headers).status_code == 403
    assert client.post("/authors", json={"name": "Иван Петров"}, headers=admin_headers).status_code == 201

    assert client.post("/books", json={"title": "Книга", "genre": "Проза"}, headers=reader_headers).status_code == 403
    created = client.post("/books", json={"title": "Чистый код", "genre": "Прогр."}, headers=admin_headers)
    assert created.status_code == 201
    assert created.json()["available_copies"] == 0


def test_get_book_and_author_by_id(client, admin_headers):
    author = client.post("/authors", json={"name": "Автор страницы"}, headers=admin_headers)
    assert author.status_code == 201
    author_id = author.json()["id"]
    assert client.get(f"/authors/{author_id}").json()["name"] == "Автор страницы"
    assert client.get("/authors/999999").status_code == 404

    created = client.post(
        "/books",
        json={
            "title": "Одна книга",
            "genre": "Проза",
            "author_ids": [author_id],
            "available_copies": 1,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201
    book_id = created.json()["id"]
    loaded = client.get(f"/books/{book_id}")
    assert loaded.status_code == 200
    assert loaded.json()["authors"][0]["id"] == author_id
    assert client.get("/books/999999").status_code == 404


def test_reader_can_read_own_profile(client, reader_headers):
    response = client.get("/users/me", headers=reader_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "reader"
    assert body["is_admin"] is False


def test_book_crud_and_date_parsing(client, admin_headers):
    created = client.post(
        "/books",
        json={
            "title": "Чистый код",
            "genre": "Программирование",
            "publication_date": "2008-08-01",
            "available_copies": 2,
        },
        headers=admin_headers,
    )
    assert created.status_code == 201
    book = created.json()
    assert book["publication_date"] == "2008-08-01"

    assert any(item["id"] == book["id"] for item in client.get("/books").json())
    assert client.delete(f"/books/{book['id']}", headers=admin_headers).status_code == 200


def test_invalid_date_returns_422(client, admin_headers):
    response = client.post(
        "/books",
        json={"title": "X", "genre": "Y", "publication_date": "not-a-date"},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_only_admin_can_add_admin(client, admin_headers, reader_headers):
    payload = {"username": "newadmin", "password": "newadmin-pass-1"}
    assert client.post("/add_admin", json=payload, headers=reader_headers).status_code == 403
    assert client.post("/add_admin", json=payload, headers=admin_headers).status_code == 200


def test_borrow_and_return_flow(client, admin_headers, reader_headers):
    book = client.post(
        "/books",
        json={"title": "Дюна", "genre": "Фантастика", "available_copies": 1},
        headers=admin_headers,
    ).json()

    reader_id = client.get("/users", headers=admin_headers).json()[0]["id"]

    # обычный пользователь не может оформлять выдачу
    denied = client.post(
        "/borrows", json={"user_id": reader_id, "book_id": book["id"]}, headers=reader_headers
    )
    assert denied.status_code == 403

    issued = client.post(
        "/borrows", json={"user_id": reader_id, "book_id": book["id"]}, headers=admin_headers
    )
    assert issued.status_code == 201
    record = issued.json()
    assert record["return_date"] is None
    assert _book_by_id(client, book["id"])["available_copies"] == 0

    # нельзя выдать ту же книгу тому же читателю повторно
    again = client.post(
        "/borrows", json={"user_id": reader_id, "book_id": book["id"]}, headers=admin_headers
    )
    assert again.status_code == 409

    # читатель видит свою выдачу и может вернуть книгу сам
    assert len(client.get("/borrows/me", headers=reader_headers).json()) == 1
    returned = client.post(f"/borrows/{record['id']}/return", headers=reader_headers)
    assert returned.status_code == 200
    assert returned.json()["return_date"] is not None
    assert _book_by_id(client, book["id"])["available_copies"] == 1

    # повторный возврат запрещён
    assert client.post(f"/borrows/{record['id']}/return", headers=reader_headers).status_code == 409


def test_cannot_borrow_book_without_copies(client, admin_headers, reader_headers):
    book = client.post(
        "/books",
        json={"title": "Редкая книга", "genre": "Редкость", "available_copies": 0},
        headers=admin_headers,
    ).json()
    reader_id = client.get("/users", headers=admin_headers).json()[0]["id"]

    response = client.post(
        "/borrows", json={"user_id": reader_id, "book_id": book["id"]}, headers=admin_headers
    )
    assert response.status_code == 409
