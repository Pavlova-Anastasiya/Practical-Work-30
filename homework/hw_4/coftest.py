import pytest
from app import create_app, db


@pytest.fixture(scope="function")
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
        }
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    yield db.session
    db.session.rollback()
