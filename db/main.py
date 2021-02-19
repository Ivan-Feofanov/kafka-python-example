import databases
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID

from config import get_settings

settings = get_settings()

database = databases.Database(settings.postgres_dsn, min_size=2, max_size=5)

metadata = sqlalchemy.MetaData()

messages = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", UUID, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("text", sqlalchemy.Text),
)

engine = sqlalchemy.create_engine(settings.postgres_dsn)

metadata.create_all(engine)
