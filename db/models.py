import uuid

from pydantic import BaseModel


class IncomingMessage(BaseModel):
    title: str
    text: str = None


class Message(BaseModel):
    id: uuid.UUID
    title: str
    text: str = None
