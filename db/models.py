from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.main import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    text = Column(Text)
    created_at = Column(
        DateTime,
        index=True,
        default=lambda: datetime.now())
    updated_at = Column(
        DateTime,
        index=True,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now())
