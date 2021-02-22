import uuid

import msgpack
import pytest

from consts import Actions
from receiver import msgpack_deserializer, create_or_update

today_uuid = str(uuid.uuid4())


@pytest.mark.parametrize('msg, success', (
        (msgpack.packb('payload'), True),
        (b'payload', False),
))
def test_msgpack_deserializer(msg, success, caplog):
    result = msgpack_deserializer(msg)
    if success is True:
        assert result == 'payload'
    else:
        assert result is None
        assert 'Unpack failed. Input: b\'payload\'' in caplog.text


@pytest.mark.parametrize('data, action, log_message', (
    ({}, Actions.UPDATE, 'Updating message without message id. Data: {}'),
    ({'id': today_uuid}, Actions.UPDATE, f'Message with id {today_uuid} '
                                         f'not found in database'),
    (None, 999, 'Unknown action 999'),
))
def test_create_or_update_logging(
        db_session, data, action, log_message, caplog):
    assert create_or_update(
        session=db_session, action=action, data=data) is None
    assert log_message in caplog.text
