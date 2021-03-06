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
    OFF = 'OFF'
    SSL = 'SSL'
    SASL = 'SASL_SSL'


class Settings(BaseSettings):
    environment: str = 'development'
    auth_token: str = None
    database_url: PostgresDsn
    kafka_url: str
    kafka_topic: str
    kafka_consumer_group: str
    kafka_auth: AuthEnum = None
    kafka_auth_ca: str = None
    kafka_auth_cert: str = None
    kafka_auth_pkey: str = None
    kafka_auth_username: str = None
    kafka_auth_password: str = None
    kafka: Dict = dict()

    class Config:
        env_file = ".env"


class TestSettings(Settings):
    kafka_url: str = None
    kafka_topic: str = None
    kafka_consumer_group: str = None


def set_kafka_auth(settings: Settings) -> Settings:
    settings.kafka = dict(
        bootstrap_servers=settings.kafka_url,
    )

    if settings.kafka_auth == AuthEnum.SASL and all([
            settings.kafka_auth_username,
            settings.kafka_auth_password]):

        settings.kafka.update({
            'security_protocol': AuthEnum.SASL,
            'sasl_mechanism': 'PLAIN',
            'sasl_plain_username': settings.kafka_auth_username,
            'sasl_plain_password': settings.kafka_auth_password,
            'ssl_cafile': os.path.join(PROJECT_DIR, settings.kafka_auth_ca)
        })

    elif settings.kafka_auth == AuthEnum.SSL and all([
            settings.kafka_auth_ca,
            settings.kafka_auth_cert,
            settings.kafka_auth_pkey]):

        settings.kafka.update({
            'security_protocol': AuthEnum.SSL,
            'ssl_certfile': os.path.join(PROJECT_DIR,
                                         settings.kafka_auth_cert),
            'ssl_keyfile': os.path.join(PROJECT_DIR, settings.kafka_auth_pkey),
            'ssl_cafile': os.path.join(PROJECT_DIR, settings.kafka_auth_ca)
        })

    return settings


@lru_cache
def get_settings() -> Settings:
    if os.environ.get('ENVIRONMENT') == 'test':
        return TestSettings()
    return set_kafka_auth(Settings())
