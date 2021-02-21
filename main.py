from functools import lru_cache
from typing import List

import msgpack
from fastapi import FastAPI, Depends
from kafka import KafkaProducer
from sqlalchemy.orm import Session

from config import get_settings
from db import models
from db.main import SessionLocal, engine
from db.schemas import Message, IncomingMessage

settings = get_settings()

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependencies
@lru_cache
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@lru_cache
def get_kafka():
    producer = KafkaProducer(
        value_serializer=msgpack.packb,
        **settings.kafka
    )
    try:
        yield producer
    finally:
        producer.close()


@app.post("/messages/")
def send(msg: IncomingMessage, producer: KafkaProducer = Depends(get_kafka)):
    producer.send(settings.kafka_topic, msg.dict())
    return msg


@app.get("/messages/", response_model=List[Message])
def read_notes(session: Session = Depends(get_db)):
    return session.query(models.Message).all()
