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

producer = KafkaProducer(
    value_serializer=msgpack.packb,
    **settings.kafka
)

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.post("/messages/")
def send(message: IncomingMessage):
    producer.send(settings.kafka_topic, message.dict())
    return message


@app.get("/messages/", response_model=List[Message])
def read_notes(session: Session = Depends(get_db)):
    return session.query(models.Message).all()
