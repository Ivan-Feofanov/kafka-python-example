import msgpack
import pytest

from receiver import msgpack_deserializer


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
