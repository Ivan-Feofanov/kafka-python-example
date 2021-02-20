from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from db.main import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String)
    text = Column(Text)
