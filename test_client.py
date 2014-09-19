import pytest
import icalendar as ic
from ticketscloud import TCClient, TCException


def test_base():
    client = TCClient(
        api_token='wrong',
        api_root='http://dev.ticketscloud.ru/')

    assert str(client.api.resources.deals) == 'GET v1/resources/deals'
    assert str(client.api.resources.deals.post) == 'POST v1/resources/deals'

    with pytest.raises(TCException):
        client.api.unknown()


def test_simple_events():
    client = TCClient(
        access_token='666666666666',
        loglevel='debug',
        api_root='http://dev.ticketscloud.ru/')
    with client.ctx(cache='test'):
        response = client.api.services.simple.events()
    assert response
    assert isinstance(response[0]['lifetime'], ic.Event)
