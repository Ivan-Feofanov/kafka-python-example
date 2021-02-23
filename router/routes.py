from typing import List
from uuid import UUID

from fastapi import Depends, APIRouter
from kafka import KafkaProducer
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from config import get_settings
from consts import Actions
from db import models, schemas
from router.dependencies import get_kafka, get_db

settings = get_settings()

api_router = APIRouter()  # noqa: pylint=invalid-name


@api_router.post('/messages/')
def create(msg: schemas.IncomingMessage,
           producer: KafkaProducer = Depends(get_kafka)):
    data = msg.dict()
    data['action'] = Actions.CREATE
    producer.send(settings.kafka_topic, data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=msg.json())


@api_router.patch("/messages/{message_id}")
def update(msg: schemas.IncomingMessage,
           message_id: UUID,
           producer: KafkaProducer = Depends(get_kafka)):
    data = msg.dict(exclude_unset=True)
    data.update({
        'id': str(message_id),
        'action': Actions.UPDATE.value
    })
    producer.send(settings.kafka_topic, data)
    return msg


@api_router.delete("/messages/{message_id}")
def delete(message_id: UUID,
           producer: KafkaProducer = Depends(get_kafka)):
    data = {
        'id': str(message_id),
        'action': Actions.DELETE.value
    }
    producer.send(settings.kafka_topic, data)


@api_router.get("/messages/", response_model=List[schemas.Message])
def read_notes(session: Session = Depends(get_db)):
    return session.query(models.Message) \
        .order_by(models.Message.created_at.desc()) \
        .all()
