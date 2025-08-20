from flask import Blueprint, jsonify, request
from . import db
from .models import Client, Parking, ClientParking

api_bp = Blueprint("api", __name__)

# --- CLIENTS ---
@api_bp.get("/clients")
def list_clients():
    return jsonify([c.to_dict() for c in Client.query.all()])

@api_bp.get("/clients/<int:client_id>")
def get_client(client_id: int):
    c = Client.query.get(client_id)
    if not c:
        return jsonify({"error": "client not found"}), 404
    return jsonify(c.to_dict())

@api_bp.post("/clients")
def create_client():
    data = request.get_json(force=True) or {}
    name, surname = data.get("name"), data.get("surname")
    if not name or not surname:
        return jsonify({"error": "name and surname required"}), 400
    c = Client(
        name=name, surname=surname,
        credit_card=data.get("credit_card"),
        car_number=data.get("car_number"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201

# --- PARKINGS ---
@api_bp.post("/parkings")
def create_parking():
    data = request.get_json(force=True) or {}
    address, count_places = data.get("address"), data.get("count_places")
    if not address or count_places is None:
        return jsonify({"error": "address and count_places required"}), 400
    p = Parking(
        address=address,
        opened=bool(data.get("opened", True)),
        count_places=int(count_places),
        count_available_places=int(data.get("count_available_places", count_places)),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

# --- ENTER / EXIT ---
@api_bp.post("/client_parkings")
def enter_parking():
    data = request.get_json(force=True) or {}
    client_id, parking_id = data.get("client_id"), data.get("parking_id")
    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id required"}), 400

    client = Client.query.get(client_id)
    parking = Parking.query.get(parking_id)
    if not client or not parking:
        return jsonify({"error": "client or parking not found"}), 404
    if not parking.opened:
        return jsonify({"error": "parking is closed"}), 400
    if parking.count_available_places <= 0:
        return jsonify({"error": "no available places"}), 400

    if ClientParking.query.filter_by(client_id=client.id, parking_id=parking.id, time_out=None).first():
        return jsonify({"error": "client already inside"}), 400

    log = ClientParking.query.filter_by(client_id=client.id, parking_id=parking.id).first()
    if not log:
        log = ClientParking(client_id=client.id, parking_id=parking.id)
        db.session.add(log)

    log.start()
    parking.count_available_places -= 1
    db.session.commit()
    return jsonify({"message": "entered", "log": log.to_dict(), "parking": parking.to_dict()}), 201

@api_bp.delete("/client_parkings")
def exit_parking():
    data = request.get_json(force=True) or {}
    client_id, parking_id = data.get("client_id"), data.get("parking_id")
    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id required"}), 400

    client = Client.query.get(client_id)
    parking = Parking.query.get(parking_id)
    log = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if not client or not parking or not log:
        return jsonify({"error": "client or parking or active log not found"}), 404
    if not client.credit_card:
        return jsonify({"error": "payment method required"}), 400

    try:
        log.finish()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    parking.count_available_places += 1
    db.session.commit()
    return jsonify({"message": "exited", "log": log.to_dict(), "parking": parking.to_dict()}), 200