from typing import List

import msgpack
from fastapi import FastAPI
from kafka import KafkaProducer

from config import get_settings
from db.main import database, messages
from db.models import Message, IncomingMessage

settings = get_settings()

producer = KafkaProducer(
    value_serializer=msgpack.packb,
    **settings.kafka
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/send")
def send(message: IncomingMessage):
    producer.send(settings.kafka_topic, message.dict())
    return message


@app.get("/messages/", response_model=List[Message])
async def read_notes():
    query = messages.select()
    return await database.fetch_all(query)
