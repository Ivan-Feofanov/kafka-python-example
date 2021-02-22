import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageBase(BaseModel):
    title: str
    text: Optional[str]


class IncomingMessage(MessageBase):
    pass


class Message(MessageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
