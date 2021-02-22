from dataclasses import dataclass
from typing import Any, Generator
from typing import Dict

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from db.main import Base
from main import get_db, get_kafka, app
from tests.session import engine, Session


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture(autouse=True, scope='session')
def test_app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create tables
    yield app
    Base.metadata.drop_all(engine)  # Drop tables


@pytest.fixture
def db_session() -> Generator[Session, Any, None]:
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)
    yield session
    Session.remove()
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


# Kafka stubs
class StubProducer:
    call_args = dict()

    def send(self, *args, **kwargs):
        self.call_args['args'] = args
        self.call_args['kwargs'] = kwargs
        pass


@dataclass
class StubMessage:
    value: Dict = None


# API client
@pytest.fixture()
def client(test_app: FastAPI, db_session: Session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    producer = StubProducer()

    def override_get_kafka():
        yield producer

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_kafka] = override_get_kafka

    client = TestClient(test_app)
    client.producer = producer
    return client
