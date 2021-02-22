import logging
import uuid
from typing import Optional, Dict

import msgpack
from kafka import KafkaConsumer
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings
from consts import Actions
from db.main import engine
from db.models import Message

settings = get_settings()
logger = logging.getLogger(__name__)


def msgpack_deserializer(msg) -> Optional[Dict]:
    try:
        return msgpack.unpackb(msg)
    except (msgpack.UnpackException, msgpack.ExtraData) as exc:
        err_msg = 'Unpack failed. Input: %s' % str(msg)
        logger.error(err_msg, exc_info=exc)


def create_or_update(session: Session, action: Actions, data: Dict
                     ) -> Optional[Message]:
    if action == Actions.CREATE:
        return Message(id=str(uuid.uuid4()), **data)
    if action == Actions.UPDATE:
        msg_id = data.get('id')
        if msg_id is None:
            logger.warning(
                'Updating message without message id. Data: %s', str(data))
            return None
        msg = session.query(Message).get(msg_id)
        if msg is None:
            logger.warning('Message with id %s not found in database', msg_id)
            return None
        for key, value in data.items():
            if value is not None:
                setattr(msg, key, value)
        return msg
    logger.warning('Unknown action %s', action)
    return None


def consume(session: Session):
    consumer = KafkaConsumer(
        settings.kafka_topic,
        group_id=settings.kafka_consumer_group,
        value_deserializer=msgpack_deserializer,
        **settings.kafka
    )

    for msg in consumer:
        action = msg.value.pop('action', None)
        if action is None:
            logger.warning('Action is None, don\'t know what to do...')
        msg_id = msg.value.get('id')
        # perform DELETE
        if action == Actions.DELETE and msg_id is not None:
            session.query(Message).filter(Message.id == msg_id).delete()
            session.commit()
            continue
        # perform CREATE or UPDATE
        db_msg = create_or_update(
            session=session,
            action=action,
            data=msg.value
        )
        if db_msg is not None:
            session.merge(db_msg, load=True)
            session.commit()


if __name__ == "__main__":
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    consume(session=SessionLocal())
