from typing import Dict, List, TypedDict, ClassVar, Any, Optional

from .http_status_constants import HttpStatusCode
from .base_objects import Response


class APIGatewayResponse(Response):
    def __init__(self, status_code: HttpStatusCode = HttpStatusCode.HTTP_STATUS_OK, body: Any = None,
                 headers=None, is_base64_encoded=False) -> None:
        """Initialize instance with list, tuple, or dict."""
        super().__init__()
        if headers is None:
            headers = {}

        self.key_map = {'status_code': 'statusCode',
                        'is_base64': 'isBase64Encoded',
                        'headers': 'headers',
                        'body': 'body'}

        self._base_headers = {
            'Access-Control-Allow-Origin': '*',
            'X-Server': 'AWS λ'
        }

        if headers and not isinstance(headers, dict):
            raise ValueError('Headers value must be dict.')
        if not isinstance(status_code, int):
            raise ValueError('Status Code value must be int.')

        self.__setattr__('headers', headers)
        self.__setattr__('status_code', int(status_code))
        self.__setattr__('body', body)
        self.__setattr__('is_base64', is_base64_encoded)

    def __setattr__(self, name, value):
        """Set attribute with some manually managed attributes."""
        # prevent recursion
        if name in ['key_map', 'store']:
            super().__setattr__(name, value)
        # process managed atts
        if name in self.key_map.keys():
            store_key = self.key_map[name]
            if name == 'headers':
                value = {**self._base_headers, **value}
            self.store[store_key] = value
        else:
            super().__setattr__(name, value)

    @property
    def serialized(self):
        return self.store
