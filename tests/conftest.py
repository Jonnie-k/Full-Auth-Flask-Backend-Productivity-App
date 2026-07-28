import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.note import Note


@pytest.fixture(scope="session")
def app():
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key-that-is-long-enough-32bytes",
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    yield _db
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


@pytest.fixture
def test_user(db):
    user = User(username="tester", email="tester@test.com")
    user.password = "password123"
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    db.session.expunge(user)
    return db.session.get(User, user_id)


@pytest.fixture
def auth_headers(client, db):
    user = User(username="tester", email="tester@test.com")
    user.password = "password123"
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/login", json={"username": "tester", "password": "password123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
