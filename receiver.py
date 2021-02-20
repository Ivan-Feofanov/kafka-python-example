import logging
import uuid
from typing import Optional, Dict

import msgpack
from kafka import KafkaConsumer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings
from db import models
from db.main import engine

settings = get_settings()
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


def msgpack_deserializer(msg) -> Optional[Dict]:
    try:
        return msgpack.unpackb(msg)
    except (msgpack.UnpackException, msgpack.ExtraData) as exc:
        logger.error(f'Unpack failed. Input: {str(msg)}', exc_info=exc)


def consume(db: Session):
    consumer = KafkaConsumer(
        settings.kafka_topic,
        group_id=f'{settings.kafka_consumer_group}-sync',
        value_deserializer=msgpack_deserializer,
        **settings.kafka
    )

    for msg in consumer:
        try:
            db_msg = models.Message(
                id=str(uuid.uuid4()),
                title=msg.value['title'],
                text=msg.value['text']
            )
            db.add(db_msg)
            db.commit()
        except SQLAlchemyError as exc:
            logger.error(msg=f'Error saving message {msg.value}', exc_info=exc)


if __name__ == "__main__":
    consume(db=session)
