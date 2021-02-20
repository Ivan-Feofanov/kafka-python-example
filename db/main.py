import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import get_settings

settings = get_settings()

if settings.environment == 'test':
    database_url = settings.test_db_dsn
else:
    database_url = settings.postgres_dsn

engine = sqlalchemy.create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
