# homework/hw_4/tests/factories.py

import factory
from faker import Faker as RealFaker

from homework.hw_4.app import db
from homework.hw_4.app.models import Client, Parking

fake = RealFaker()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        # не коммитим автоматически — только flush,
        # чтобы можно было управлять транзакцией в тестах
        sqlalchemy_session_persistence = "flush"


class ClientFactory(BaseFactory):
    class Meta:
        model = Client

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    _has_card = factory.Faker("pybool")
    # если флаг _has_card истинен — генерим номер карты, иначе None
    credit_card = factory.LazyAttribute(
        lambda o: fake.credit_card_number() if o._has_card else None
    )
    # условный номер авто вида ABC123
    car_number = factory.Faker("bothify", text="???###")


class ParkingFactory(BaseFactory):
    class Meta:
        model = Parking

    address = factory.Faker("address")
    opened = factory.Faker("pybool")
    count_places = factory.Faker("pyint", min_value=1, max_value=50)
    # по умолчанию все места доступны
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)
