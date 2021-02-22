from functools import lru_cache
from typing import List
from uuid import UUID

import msgpack
from fastapi import FastAPI, Depends
from kafka import KafkaProducer
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from config import get_settings
from consts import Actions
from db import models
from db.main import SessionLocal, engine
from db.schemas import Message, IncomingMessage

settings = get_settings()

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


@app.middleware("http")
async def check_security_token(request: Request, call_next):
    if settings.environment == 'production':
        auth_token = request.headers.get('Authorization')
        if auth_token != settings.auth_token or auth_token is None:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    response = await call_next(request)
    return response


@app.on_event("shutdown")
def shutdown_event():
    producer = get_kafka()
    producer.close()


@app.post('/messages/')
def create(msg: IncomingMessage, producer: KafkaProducer = Depends(get_kafka)):
    data = msg.dict()
    data['action'] = Actions.CREATE
    producer.send(settings.kafka_topic, data)
    return msg


@app.patch("/messages/{message_id}")
def update(msg: IncomingMessage,
           message_id: UUID,
           producer: KafkaProducer = Depends(get_kafka)):
    data = msg.dict(exclude_unset=True)
    data.update({
        'id': str(message_id),
        'action': Actions.UPDATE.value
    })
    producer.send(settings.kafka_topic, data)
    return msg


@app.delete("/messages/{message_id}")
def delete(message_id: UUID,
           producer: KafkaProducer = Depends(get_kafka)):
    data = {
        'id': str(message_id),
        'action': Actions.DELETE.value
    }
    producer.send(settings.kafka_topic, data)


@app.get("/messages/", response_model=List[Message])
def read_notes(session: Session = Depends(get_db)):
    return session.query(models.Message)\
        .order_by(models.Message.created_at.desc())\
        .all()
