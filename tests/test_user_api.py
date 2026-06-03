from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import create_app


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app = create_app(init_database=False)
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as test_client:
        yield test_client
    test_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_user(client: TestClient) -> None:
    response = client.post("/api/users", json={"name": "Ada", "age": 36, "job": "Engineer"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Ada", "age": 36, "job": "Engineer"}


def test_list_users(client: TestClient) -> None:
    client.post("/api/users", json={"name": "Ada", "age": 36, "job": "Engineer"})
    client.post("/api/users", json={"name": "Grace", "age": 40, "job": "Scientist"})

    response = client.get("/api/users")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Ada", "age": 36, "job": "Engineer"},
        {"id": 2, "name": "Grace", "age": 40, "job": "Scientist"},
    ]


def test_get_user_by_id(client: TestClient) -> None:
    created = client.post("/api/users", json={"name": "Ada", "age": 36, "job": "Engineer"})

    response = client.get(f"/api/users/{created.json()['id']}")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Ada", "age": 36, "job": "Engineer"}


def test_update_user(client: TestClient) -> None:
    created = client.post("/api/users", json={"name": "Ada", "age": 36, "job": "Engineer"})

    response = client.put(
        f"/api/users/{created.json()['id']}",
        json={"name": "Ada Lovelace", "age": 37, "job": "Mathematician"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Ada Lovelace",
        "age": 37,
        "job": "Mathematician",
    }


def test_delete_user(client: TestClient) -> None:
    created = client.post("/api/users", json={"name": "Ada", "age": 36, "job": "Engineer"})

    response = client.delete(f"/api/users/{created.json()['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/users/{created.json()['id']}").status_code == 404


def test_missing_user_returns_404(client: TestClient) -> None:
    assert client.get("/api/users/999").status_code == 404
    assert client.put("/api/users/999", json={"name": "Ada", "age": 36, "job": "Engineer"}).status_code == 404
    assert client.delete("/api/users/999").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "age": 36, "job": "Engineer"},
        {"name": "Ada", "age": -1, "job": "Engineer"},
        {"name": "Ada", "age": 36, "job": ""},
    ],
)
def test_invalid_user_input_returns_422(client: TestClient, payload: dict[str, object]) -> None:
    response = client.post("/api/users", json=payload)

    assert response.status_code == 422
