import uuid
from datetime import datetime

import factory.fuzzy
from factory.alchemy import SQLAlchemyModelFactory

from db.models import Message
from tests.session import Session


class MessageFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Message
        sqlalchemy_session = Session

    id = str(uuid.uuid4())
    title = factory.fuzzy.FuzzyText()
    text = factory.fuzzy.FuzzyText()
    created_at: datetime = None
    updated_at: datetime = None
