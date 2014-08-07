import pytest


def test_base():
    from ticketscloud import TCClient, TCException

    client = TCClient(api_token='wrong', api_root='http://dev.ticketscloud.ru/')

    assert str(client.api.resources.deals) == 'GET v1/resources/deals'
    assert str(client.api.resources.deals.post) == 'POST v1/resources/deals'

    with pytest.raises(TCException):
        client.api.unknown()
