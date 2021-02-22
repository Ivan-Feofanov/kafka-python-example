from functools import lru_cache

import msgpack
from kafka import KafkaProducer

from config import get_settings
from db.main import SessionLocal

settings = get_settings()


# Dependencies
# One session per request
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# One Kafka producer for all requests
@lru_cache
def get_kafka():
    producer = KafkaProducer(
        value_serializer=msgpack.packb,
        **settings.kafka
    )
    return producer
