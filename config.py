import os
from functools import lru_cache
from typing import Dict

from pydantic import BaseSettings, PostgresDsn

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    app_name: str = "Aiven Kafka usage example"
    root_dir: str = PROJECT_DIR
    postgres_dsn: PostgresDsn
    kafka_dsn: str
    kafka_topic: str
    kafka_consumer_group: str
    kafka_auth_ca: str
    kafka_auth_cert: str
    kafka_auth_pkey: str
    kafka: Dict = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    settings = Settings()

    # set absolute paths for kafka credentials
    settings.kafka_auth_ca = os.path.join(
        settings.root_dir, settings.kafka_auth_ca)
    settings.kafka_auth_cert = os.path.join(
        settings.root_dir, settings.kafka_auth_cert)
    settings.kafka_auth_pkey = os.path.join(
        settings.root_dir, settings.kafka_auth_pkey)

    settings.kafka = dict(
        bootstrap_servers=[settings.kafka_dsn],
        security_protocol="SSL",
        ssl_cafile=settings.kafka_auth_ca,
        ssl_certfile=settings.kafka_auth_cert,
        ssl_keyfile=settings.kafka_auth_pkey
    )
    return settings
