from unittest import mock

import pytest
from freezegun import freeze_time
from starlette import status

from db.models import Message
from receiver import consume
from tests.conftest import StubMessage
from tests.factories import MessageFactory


def test_api_post(db_session, client, faker):
    user_data = {
        'title': faker.pystr(),
        'text': faker.pystr()
    }
    res = client.post('/messages/', json=user_data)
    assert res.status_code == status.HTTP_200_OK

    msg_data = client.producer.call_args['args'][1]
    with mock.patch('receiver.KafkaConsumer',
                    return_value=[StubMessage(value=msg_data)]):
        consume(session=db_session)

    res = client.get("/messages/")
    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data[0]['id'] is not None
    assert data[0]['created_at'] is not None
    assert data[0]['updated_at'] is not None
    assert data[0]['title'] == user_data['title']
    assert data[0]['text'] == user_data['text']


@pytest.mark.parametrize('partial', (True, False))
def test_api_patch(db_session, client, faker, partial):
    msg: MessageFactory = MessageFactory()
    assert db_session.query(Message).count() == 1
    old_text = msg.text
    new_data = {
        'title': faker.pystr(),
        'text': faker.pystr()
    }
    if partial:
        del new_data['text']

    res = client.patch(f'/messages/{msg.id}', json=new_data)
    assert res.status_code == status.HTTP_200_OK

    msg_data = client.producer.call_args['args'][1]
    with mock.patch('receiver.KafkaConsumer',
                    return_value=[StubMessage(value=msg_data)]):
        consume(session=db_session)

    assert db_session.query(Message).count() == 1

    new_msg: Message = db_session.query(Message).first()

    res = client.get('/messages/')
    data = res.json()[0]

    assert data['id'] == msg.id
    assert data['created_at'] == msg.created_at.isoformat()
    assert new_msg.updated_at > new_msg.created_at
    assert new_msg.title == new_data['title']
    if not partial:
        assert new_msg.text == new_data['text']
    else:
        assert new_msg.text == old_text


def test_api_delete(db_session, client):
    msg: MessageFactory = MessageFactory()
    assert db_session.query(Message).get(msg.id) is not None

    res = client.delete(f'/messages/{msg.id}')
    assert res.status_code == status.HTTP_200_OK

    msg_data = client.producer.call_args['args'][1]
    with mock.patch('receiver.KafkaConsumer',
                    return_value=[StubMessage(value=msg_data)]):
        consume(session=db_session)

    assert db_session.query(Message).get(msg.id) is None


def test_api_ordering(client):
    with freeze_time('2000-01-01'):
        msg_old: MessageFactory = MessageFactory()
    msg_new: MessageFactory = MessageFactory()

    res = client.get('/messages/')
    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data[0]['id'] == str(msg_new.id)
    assert data[1]['id'] == str(msg_old.id)

