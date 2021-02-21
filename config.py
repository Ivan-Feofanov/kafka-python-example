import os
from enum import Enum
from functools import lru_cache
from typing import Dict

from pydantic import BaseSettings, PostgresDsn

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
BASE_DIR_NAME = os.path.basename(BASE_DIR)
SERVICE_NAME = os.environ.get('SERVICE_NAME', BASE_DIR_NAME)


class AuthEnum(str, Enum):
    off = 'off'
    ssl = 'ssl'
    basic = 'basic'


class Settings(BaseSettings):
    root_dir: str = PROJECT_DIR
    database_url: PostgresDsn
    kafka_url: str
    kafka_topic: str
    kafka_consumer_group: str
    kafka_auth: AuthEnum = None
    kafka_auth_ca: str = None
    kafka_auth_cert: str = None
    kafka_auth_pkey: str = None
    kafka: Dict = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    settings = Settings()

    settings.kafka = dict(bootstrap_servers=settings.kafka_url)

    # TODO: add password auth
    if settings.kafka_auth == 'ssl' and all([settings.kafka_auth_ca,
                                             settings.kafka_auth_cert,
                                             settings.kafka_auth_pkey]):
        settings.kafka['security_protocol'] = 'SSL'
        settings.kafka['ssl_cafile'] = os.path.join(
            settings.root_dir, settings.kafka_auth_ca)
        settings.kafka['ssl_certfile'] = os.path.join(
            settings.root_dir, settings.kafka_auth_cert)
        settings.kafka['ssl_keyfile'] = os.path.join(
            settings.root_dir, settings.kafka_auth_pkey)

    return settings
