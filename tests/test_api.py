from unittest import mock

from starlette import status

from receiver import consume
from tests.conftest import StubMessage


def test_api(session, client, faker):
    user_data = {
        'title': faker.pystr(),
        'text': faker.pystr()
    }
    res = client.post('/messages/', json=user_data)
    assert res.status_code == status.HTTP_200_OK

    with mock.patch('receiver.KafkaConsumer',
                    return_value=[StubMessage(value=user_data)]):
        consume(session=session)

    response = client.get("/messages/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]['id'] is not None
    assert data[0]['title'] == user_data['title']
    assert data[0]['text'] == user_data['text']
