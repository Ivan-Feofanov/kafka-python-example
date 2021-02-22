from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import get_settings

"""
Create scoped session for factories
https://docs.sqlalchemy.org/en/14/orm/contextual.html#unitofwork-contextual
https://factoryboy.readthedocs.io/en/stable/orms.html#managing-sessions
"""
settings = get_settings()
engine = create_engine(settings.database_url)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
