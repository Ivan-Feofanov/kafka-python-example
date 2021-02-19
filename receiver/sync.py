import logging
import uuid
from typing import Optional, Dict

import msgpack
from kafka import KafkaConsumer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from config import get_settings
from db.main import messages, engine

settings = get_settings()
logger = logging.getLogger(__name__)

# DB stuff
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


def msgpack_deserializer(msg) -> Optional[Dict]:
    try:
        return msgpack.unpackb(msg)
    except (msgpack.UnpackException, msgpack.ExtraData) as exc:
        logger.error(f'Unpack failed. Input: {str(msg)}', exc_info=exc)


consumer = KafkaConsumer(
    settings.kafka_topic,
    group_id=f'{settings.kafka_consumer_group}-sync-2',
    value_deserializer=msgpack_deserializer,
    **settings.kafka
)

for msg in consumer:
    msg.value.update(id=str(uuid.uuid4()))
    try:
        res = db.execute(messages.insert(), params=msg.value)
        db.commit()
    except (SQLAlchemyError, TypeError) as exc:
        logger.error(exc)
