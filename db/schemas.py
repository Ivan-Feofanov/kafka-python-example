import uuid

from pydantic import BaseModel


class MessageBase(BaseModel):
    title: str
    text: str = None


class IncomingMessage(MessageBase):
    pass


class Message(MessageBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
