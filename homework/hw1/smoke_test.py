from app import create_app, db
from app.models import Client, Parking, ClientParking

app = create_app()
with app.app_context():
    db.create_all()

    c = Client(name="Ivan", surname="Ivanov", credit_card="4242 4242", car_number="ABC123")
    p = Parking(address="Main st, 1", opened=True, count_places=10, count_available_places=10)
    db.session.add_all([c, p]); db.session.commit()

    log = ClientParking(client_id=c.id, parking_id=p.id)
    log.start()
    db.session.add(log); db.session.commit()

    print("Client ID:", c.id, "Parking ID:", p.id, "Log ID:", log.id)
