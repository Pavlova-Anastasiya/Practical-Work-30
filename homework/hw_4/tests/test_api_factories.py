import factory
import pytest

from homework.hw_4.app import db
from homework.hw_4.app.models import Client, Parking
from homework.hw_4.tests.factories import ClientFactory, ParkingFactory


@pytest.mark.usefixtures("app")
def test_create_client_via_factory(client, app):
    payload = factory.build(dict, FACTORY_CLASS=ClientFactory)
    payload["name"] = payload.get("name") or "Ivan"
    payload["surname"] = payload.get("surname") or "Ivanov"

    r = client.post("/clients", json=payload)
    assert r.status_code == 201
    new_id = r.get_json()["id"]
    assert new_id > 0

    # проверка в контексте приложения
    with app.app_context():
        assert db.session.get(Client, new_id) is not None


@pytest.mark.usefixtures("app")
def test_create_parking_via_factory(client, app):
    payload = factory.build(dict, FACTORY_CLASS=ParkingFactory)
    payload["count_places"] = max(1, int(payload.get("count_places", 1)))

    r = client.post("/parkings", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] > 0
    assert data["count_available_places"] == data["count_places"]

    # проверка в контексте приложения
    with app.app_context():
        assert db.session.get(Parking, data["id"]) is not None
