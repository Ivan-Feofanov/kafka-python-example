import pytest
from faker import Faker
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from db.main import engine
from main import app, get_db


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


Session = sessionmaker()


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
