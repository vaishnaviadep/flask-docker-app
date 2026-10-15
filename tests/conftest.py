import pytest

from app import app, get_conn


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE tasks RESTART IDENTITY")
    with app.test_client() as c:
        yield c