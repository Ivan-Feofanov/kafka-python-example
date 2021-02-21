from dataclasses import dataclass
from typing import Dict

import pytest
from faker import Faker
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from db.main import engine
from main import app, get_db, get_kafka


class StubProducer:
    def send(self, *args, **kwargs):
        pass


@dataclass
class StubMessage:
    value: Dict = None


@pytest.fixture(scope='session')
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker()(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    def override_get_kafka():
        yield StubProducer()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_kafka] = override_get_kafka

    return TestClient(app)

