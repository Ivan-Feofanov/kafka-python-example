import asyncio
import logging
import uuid
from typing import Optional, Dict

import msgpack
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
from databases import Database
from sqlalchemy.exc import SQLAlchemyError

from config import get_settings
from db.main import messages

settings = get_settings()
database = Database(settings.postgres_dsn)
logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()


def msgpack_deserializer(msg) -> Optional[Dict]:
    try:
        return msgpack.unpackb(msg)
    except (msgpack.UnpackException, msgpack.ExtraData) as exc:
        logger.error(f'Unpack failed. Input: {str(msg)}', exc_info=exc)


context = create_ssl_context(
    cafile=settings.kafka_auth_ca,
    certfile=settings.kafka_auth_cert,
    keyfile=settings.kafka_auth_pkey,
)


async def consume():
    consumer = AIOKafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=[settings.kafka_dsn],
        group_id=f'{settings.kafka_consumer_group}-async',
        value_deserializer=msgpack_deserializer,
        security_protocol="SSL",
        ssl_context=context
    )

    await consumer.start()
    await database.connect()

    try:
        async for msg in consumer:
            msg.value.update(id=uuid.uuid4())
            query = messages.insert()
            try:
                await database.execute(query=query, values=msg.value)
            except SQLAlchemyError as exc:
                logger.error(exc)
    finally:
        await consumer.stop()
        await database.disconnect()

loop.run_until_complete(consume())
