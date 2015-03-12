"""

Ticketscloud description.

in process

"""
import re
import icalendar as ic
import ujson as json
import logging
import requests as rs
import requests_cache as rc # noqa
from contextlib import contextmanager
from functools import wraps
import decimal as dc


# Package information
# ===================
__version__ = "0.6.2"
__project__ = "ticketscloud"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "BSD"


logger = logging.getLogger(__name__)
rs_logger = logging.getLogger('requests')

if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def _curry_method(method, *cargs, **ckwargs):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        args = cargs + args
        kwargs.update(ckwargs)
        return method(self, *args, **kwargs)

    return wrapper


class TCException(Exception):

    """ Implement the TC API exception. """

    pass


class TCAPIDescriptor(object):

    """ Proxy the TC API methods. """

    __methods = 'get', 'post', 'put', 'patch', 'delete', 'head'
    __rules = {}

    def __init__(self, client):
        self.__client = client
        self.__method = 'GET'
        self.__session = []
        version = client.options.get('api_version')
        if version:
            self.__session.append(version)

    @property
    def __url(self):
        """ Return self url. """
        return "/".join(self.__session)

    def __getattr__(self, method):
        method = str(method)
        if method.lower() in self.__methods:
            self.__method = method.upper()
        else:
            self.__session.append(method)
        return self

    __getitem__ = __getattr__

    def __str__(self):
        return "%s %s" % (self.__method, self.__url)

    def __repr__(self):
        return 'API %s' % self

    def __call__(self, **data):
        """ Make request to ticketscloud. """

        client = self.__client
        method = self.__method
        url = self.__url
        prepare = self.__prepare

        kwargs = dict(data=data)
        if method.lower() == 'get':
            data = dict(
                (k, v if not isinstance(v, (list, tuple)) else ','.join(v))
                for (k, v) in data.items())
            kwargs = dict(params=data)

        if client.options['raw']:
            url, params, headers, data = client.prepare(
                url, kwargs.get('params'), kwargs.get('headers'), data)
            return method, url, params, headers, data, prepare

        response = self.__client.request(self.__method, self.__url, **kwargs)
        return prepare(response)

    def __prepare(self, data):
        for reg, func in self.__rules.items():
            if reg.match(self.__url):
                return func(data)
        return data

    @classmethod
    def __rule__(cls, reg):
        reg = re.compile(reg)

        def wrapper(func):
            if func:
                cls.__rules[reg] = func
            return func
        return wrapper


class TCClient(object):

    """ Client for the TC API. """

    exception = TCException
    cache_installed = False

    default_options = dict(
        accept='application/json',
        access_token=None,
        api_root='https://ticketscloud.org',
        api_version='v1',
        cache=None,
        loglevel='info',
        raw=False,
        user_agent='TC-Client v.%s' % __version__,
    )

    def __init__(self, **options):
        self.options = dict(self.default_options)
        self.options.update(options)

    @property
    def headers(self):
        """ Get default request headers. """
        return {
            'Accept': self.options['accept'],
            'Authorization': "key %s" % self.options['access_token'],
            'User-Agent': self.options['user_agent'],
            'Content-type': 'application/json',
        }

    def prepare(self, url, params, headers, data):
        loglevel = self.options.get('loglevel', 'info')
        logger.setLevel(loglevel.upper())
        rs_logger.setLevel(loglevel.upper())
        logger.debug("Params: %s", params)
        logger.debug("Data: %s", data)

        url = '%s/%s' % (self.options['api_root'], url.strip('/'))

        _headers = self.headers
        if headers is not None:
            _headers.update(headers)

        logger.debug("Headers: %s", _headers)

        if data is not None:
            data = json.dumps(data)

        return url, params, _headers, data

    def request(self, method, url, params=None, headers=None, to_json=True, data=None, **kwargs):
        """ Make request to TC API. """

        url, params, headers, data = self.prepare(url, params, headers, data)

        if self.options['cache']:
            rc.install_cache(self.options['cache'])

        elif type(self).cache_installed:
            rc.uninstall_cache()

        type(self).cache_installed = bool(self.options['cache'])

        try:
            response = rs.api.request(
                method, url, params=params, headers=headers, data=data, **kwargs)
            logger.debug(response.content)
            response.raise_for_status()
            if to_json:
                response = response.json()

        except (ValueError, rs.HTTPError):
            if locals().get('response') is not None:
                message = "%s: %s" % (response.status_code, response.content)
                raise TCException(message)
            raise

        return response

    get = _curry_method(request, 'GET')
    post = _curry_method(request, 'POST')
    put = _curry_method(request, 'PUT')
    head = _curry_method(request, 'HEAD')
    patch = _curry_method(request, 'PATCH')
    delete = _curry_method(request, 'DELETE')

    @contextmanager
    def ctx(self, **options):
        """ Redefine context. """
        _opts = dict(self.options)
        try:
            self.options.update(options)
            yield self
        finally:
            self.options = _opts
            if not self.options['cache'] and type(self).cache_installed:
                rc.uninstall_cache()

    @property
    def api(self):
        return TCAPIDescriptor(self)


@TCAPIDescriptor.__rule__(r'^v1/services/simple/events$')
def construct_simple_events(data):
    """ Transform Events' data. """
    for dd in data:
        construct_event(dd)
    return data


@TCAPIDescriptor.__rule__(r'^v1/services/simple/events/[^/]+$')
def construct_simple_event(data):
    """ Transform Event data. """
    return construct_event(data)


@TCAPIDescriptor.__rule__(r'^v1/resources/events/[^/]+$')
def construct_event(data):
    """ Transform Event's data. """
    data['lifetime'] = ic.Calendar().from_ical(data.get('lifetime', ''))
    data['sets'] = construct_sets(data['sets'])
    return data


@TCAPIDescriptor.__rule__(r'^v1/resources/events/[^/]+/sets$')
def construct_sets(data):
    """ Transform Sets' data. """
    return [construct_set(e) for e in data]


@TCAPIDescriptor.__rule__(r'^v1/resources/events/[^/]+/sets/[^/]+$')
def construct_set(data):
    """ Transform Set's data. """
    data['price'] = dc.Decimal(data.get('price', '0'))
    data['price_org'] = dc.Decimal(data.get('price_org', '0'))
    data['rules'] = [construct_rule(r) for r in data['rules']]
    return data


@TCAPIDescriptor.__rule__(r'^v1/resources/events$')
def construct_events(data):
    """ Transform Events' data. """
    return [construct_event(e) for e in data]


def construct_rule(data):
    """ Transform Rule data. """
    data['price'] = dc.Decimal(data.get('price', '0'))
    data['price_org'] = dc.Decimal(data.get('price_org', '0'))
    try:
        data['cal'] = ic.Calendar().from_ical(data.get('cal', ''))
    except ValueError:
        pass
    return data
