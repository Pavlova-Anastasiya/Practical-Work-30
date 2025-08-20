import pytest


# --- Все GET-методы возвращают 200 ---
@pytest.mark.parametrize("url", [
    "/clients",
    "/clients/1",   # клиент из фикстуры app
])
def test_gets_return_200(client, url):
    r = client.get(url)
    assert r.status_code == 200

# --- Создание клиента ---
def test_create_client(client):
    payload = {"name": "Petr", "surname": "Petrov", "car_number": "KZ001AB"}
    r = client.post("/clients", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] > 0
    assert data["name"] == "Petr"
    assert data["surname"] == "Petrov"

# --- Создание парковки ---
def test_create_parking(client):
    r = client.post("/parkings", json={"address": "2nd ave, 5", "count_places": 3})
    assert r.status_code == 201
    data = r.get_json()
    assert data["count_places"] == 3
    assert data["count_available_places"] == 3  # по умолчанию = count_places

# --- Заезд на парковку ---
@pytest.mark.parking
def test_enter_parking(client):
    r = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert r.status_code == 201
    data = r.get_json()
    assert data["log"]["time_in"] is not None
    assert data["log"]["time_out"] is None
    # свободных мест стало меньше
    assert data["parking"]["count_available_places"] == 9

# --- Выезд с парковки ---
@pytest.mark.parking
def test_exit_parking(client):
    # сначала заезд
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    # теперь выезд
    r = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert r.status_code == 200
    data = r.get_json()
    assert data["log"]["time_out"] is not None
    # свободных мест снова 10
    assert data["parking"]["count_available_places"] == 10