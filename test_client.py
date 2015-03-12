import sys

import icalendar as ic
import pytest

from ticketscloud import TCClient, TCException


@pytest.mark.skipif(sys.version_info < (3, 0), reason="skip if python2")
def test_raw():
    client = TCClient(
        access_token='666666666666',
        api_root='http://dev.ticketscloud.ru/',
        raw=True,
        loglevel='debug',
    )

    method, url, params, headers, data, prepare = client.api.services.simple.events()
    assert data == '{}'
    assert headers
    assert method == 'GET'
    assert params == {}
    assert prepare({}) == params
    assert url


def test_base():
    client = TCClient(
        api_token='wrong',
        api_root='http://dev.ticketscloud.ru/')

    assert str(client.api.resources.deals) == 'GET v1/resources/deals'
    assert str(client.api.resources.deals.post) == 'POST v1/resources/deals'

    with pytest.raises(TCException):
        client.api.unknown()


@pytest.mark.skipif(sys.version_info >= (3, 0), reason="skip if python3")
def test_simple_events():
    client = TCClient(
        access_token='666666666666',
        loglevel='debug',
        api_root='http://dev.ticketscloud.ru/')
    with client.ctx(cache='test'):
        response = client.api.services.simple.events()
    assert response
    assert isinstance(response[0]['lifetime'], ic.Event)
