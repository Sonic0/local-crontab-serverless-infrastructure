from typing import Dict, TypedDict, Optional, Union
from collections import namedtuple
import functools
import inflection
import base64
import json

from .base_objects import Request


class APIGatewayRequest(Request):
    """API Gateway Request class."""

    def __init__(self, event, context):
        super().__init__(event, context)
        self._body_binary = base64.b64decode(event.get('body', None))
        self._body = json.loads(self._body_binary.decode(encoding="utf-8", errors="strict"))
        self._http_method = event.get('httpMethod', 'GET')
        self._resource = event.get('resource')
        self._path_parameters = event.get('pathParameters', {})
        self._query_parameters = event.get('queryStringParameters', {})
        self._request_context = event.get('requestContext', {})
        self._headers = event.get('headers', {})

    @functools.cached_property
    def body(self):
        """Return body. The output is the same as the input type"""
        return self._body  # None if nothing from ApiGateway

    @functools.cached_property
    def headers(self):
        """Return request headers as namedtuple."""
        payload = {inflection.underscore(
            k): v for k, v, in self._headers.items()}
        HeadersTuple = namedtuple('HeadersTuple', sorted(payload))
        the_tuple = HeadersTuple(**payload)
        return the_tuple

    @functools.cached_property
    def http(self):
        """Return request http method as namedtuple."""
        return str(self._http_method)

    @functools.cached_property
    def resource(self):
        """Return request http method as namedtuple."""
        return str(self._resource)

    @functools.cached_property
    def path(self):
        """Return request path parameters as namedtuple."""
        if bool(self._path_parameters):
            payload = {inflection.underscore(k): v for k, v, in self._path_parameters.items()}
        else:
            payload = dict()
        PathTuple = namedtuple('PathTuple', sorted(payload))
        the_tuple = PathTuple(**payload)
        return the_tuple

    @functools.cached_property
    def query(self):
        """Return request query string as namedtuple."""
        if bool(self._query_parameters):  # ApiGateway set key value None in case of absence params, not an empty dict
            payload = {inflection.underscore(k): v for k, v, in self._query_parameters.items()}
        else:
            payload = dict()
        QueryTuple = namedtuple('QueryTuple', sorted(payload))
        the_tuple = QueryTuple(**payload)
        return the_tuple
