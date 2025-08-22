from datetime import datetime

from typing import TYPE_CHECKING
from . import db

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

    db: SQLAlchemy


class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))


class Parking(db.Model):
    __tablename__ = "parking"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)


class ClientParking(db.Model):
    __tablename__ = "client_parking"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),)

    def start(self):
        self.time_in = datetime.utcnow()
        self.time_out = None

    def finish(self):
        now = datetime.utcnow()
        if self.time_in and now < self.time_in:
            raise ValueError("time_out earlier than time_in")
        self.time_out = now
