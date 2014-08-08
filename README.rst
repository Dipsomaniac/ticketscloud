Ticketscloud API Client
#######################

.. _description:

Ticketscloud API Client -- A python client for API ticketscloud.ru

.. _badges:

.. image:: https://secure.travis-ci.org/Dipsomaniac/ticketscloud.png?branch=develop
    :target: http://travis-ci.org/Dipsomaniac/ticketscloud
    :alt: Build Status

.. image:: https://pypip.in/d/ticketscloud/badge.png
    :target: https://pypi.python.org/pypi/ticketscloud

.. image:: https://badge.fury.io/py/ticketscloud.png
    :target: http://badge.fury.io/py/ticketscloud

.. _documentation:

**Docs are available at https://ticketscloud.readthedocs.org/. Pull requests
with documentation enhancements and/or fixes are awesome and most welcome.**

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 2.6

.. _installation:

Installation
=============

**Ticketscloud API Client** could be installed using pip: ::

    pip install ticketscloud

.. _usage:

Usage
=====

Initialize API client
---------------------

You should have `api_token`, from the TC service.

::

    from ticketscloud import TCClient

    client = TCClient(api_token='your-token-here')


Customize options
-----------------
::

    client = TCClient(
        access_token='your-token-here',
        api_root='http://ticketscloud.ru',
        api_version='v1',
        loglevel='info',
        user_agent='TC-Client',
    )


Working with TC API
-------------------

The client has nice and easy syntax. Just have a look: ::

    # Get events list GET http://ticketscloud.ru/v1/resources/events
    client.api.resources.events()
    client.api.resources.events['event-id']()

    # Get deals list with scheme GET http://ticketscloud.ru/v1/resources/deals
    client.api.resources.deals(**{
        'fields-schema': 'id,event{id},term{extra}', 'status': 'accepted'})

    # Create a new order POST http://ticketscloud.ru/v1/resources/orders/
    client.api.resources.orders.post(total=..., event=...)

    # Update a order PATCH http://ticketscloud.ru/v1/resources/orders/<id>
    client.api.resources.orders['id'].patch(status=)

    # You could also use a 'getitem' syntax for resources
    client.api.resources['custom-resource-name'](**params)
    # Same there
    client.api['resources']['custom-resource-name'](**params)

    # And etc. I hope you make decision how the client works :)

Context manager
---------------

You could temporary redefine the client settings in context: ::

    with client.ctx(loglevel='DEBUG'):
        # More logging here
        client.api.resources.deals(**params)


Raw api request
---------------

You could make a raw request to TC API: ::

    client.request(method='GET', url='v1/resources/events', data={...})


Have a nice codding!

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/Dipsomaniac/ticketscloud/issues

.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/Dipsomaniac/ticketscloud


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
=======

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.io/
