from datetime import datetime, timedelta

import pytest
from app import create_app, db
from app.models import Client, ClientParking, Parking


@pytest.fixture(scope="function")
def app():
    """Тестовое приложение + свежая БД на каждый тест."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            # для in-memory SQLite внутри тестового клиента
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
        }
    )
    with app.app_context():
        db.create_all()

        # Базовые записи для тестов
        c = Client(
            name="Ivan", surname="Ivanov", credit_card="4242 4242 4242 4242", car_number="ABC123"
        )
        p = Parking(address="Main st, 1", opened=True, count_places=10, count_available_places=10)
        db.session.add_all([c, p])
        db.session.flush()  # чтобы были id

        # завершённый прошлый визит — просто для данных
        log = ClientParking(client_id=c.id, parking_id=p.id)
        log.time_in = datetime.utcnow() - timedelta(hours=2)
        log.time_out = datetime.utcnow() - timedelta(hours=1)
        db.session.add(log)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    """HTTP-клиент Flask для запросов к API."""
    return app.test_client()


@pytest.fixture()
def db_session(app):
    """Доступ к сессии БД, если в тесте нужно заглянуть в таблицы напрямую."""
    yield db.session
    db.session.rollback()
