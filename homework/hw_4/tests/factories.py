import factory
from app import db
from app.models import Client, Parking
from factory import Faker, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"  # не коммитим автоматически

class ClientFactory(BaseFactory):
    class Meta:
        model = Client

    name = Faker("first_name")
    surname = Faker("last_name")
    _has_card = Faker("pybool")  # карта может быть, а может и нет
    credit_card = LazyAttribute(
        lambda o: Faker("credit_card_number").generate({}) if o._has_card else None
    )
    car_number = Faker("bothify", text="???###")  # типа ABC123

class ParkingFactory(BaseFactory):
    class Meta:
        model = Parking

    address = Faker("address")
    opened = Faker("pybool")
    count_places = Faker("pyint", min_value=1, max_value=50)
    count_available_places = LazyAttribute(lambda o: o.count_places)  # по умолчанию все свободны
