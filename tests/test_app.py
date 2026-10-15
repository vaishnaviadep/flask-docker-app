def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["message"] == "Task Manager API is running"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_list_empty(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_task(client):
    r = client.post("/tasks", json={"title": "Learn Docker"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] == 1
    assert data["title"] == "Learn Docker"
    assert data["done"] is False


def test_create_task_missing_title(client):
    r = client.post("/tasks", json={})
    assert r.status_code == 400
    assert r.get_json()["error"] == "title is required"


def test_create_task_no_body(client):
    r = client.post("/tasks")
    assert r.status_code == 400


def test_list_after_create(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    r = client.get("/tasks")
    titles = [t["title"] for t in r.get_json()]
    assert titles == ["Task A", "Task B"]


def test_toggle_task(client):
    client.post("/tasks", json={"title": "Task A"})
    r = client.put("/tasks/1")
    assert r.status_code == 200
    assert r.get_json()["done"] is True


def test_toggle_twice_returns_to_false(client):
    client.post("/tasks", json={"title": "Task A"})
    client.put("/tasks/1")
    r = client.put("/tasks/1")
    assert r.get_json()["done"] is False


def test_toggle_nonexistent_task(client):
    r = client.put("/tasks/999")
    assert r.status_code == 404


def test_delete_task(client):
    client.post("/tasks", json={"title": "Task A"})
    r = client.delete("/tasks/1")
    assert r.status_code == 200
    assert client.get("/tasks").get_json() == []


def test_delete_nonexistent_task(client):
    r = client.delete("/tasks/999")
    assert r.status_code == 404