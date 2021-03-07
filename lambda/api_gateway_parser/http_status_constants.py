from enum import IntEnum


class HttpStatusCode(IntEnum):
    """ Http Status Codes """
    HTTP_STATUS_OK = 200  # The request has succeeded
    HTTP_STATUS_BAD_REQUEST = 400  # This response means that server could not understand the request due to invalid syntax.
    HTTP_STATUS_UNAUTHORIZED = 401  # The client must authenticate itself to get the requested response.
    HTTP_STATUS_FORBIDDEN = 403  # The client does not have access rights to the content, i.e. they are unauthorized.
    HTTP_STATUS_NOT_FOUND = 404  # The server can not find requested resource.
    HTTP_STATUS_INTERNAL_SERVER_ERROR = 500  # The server has encountered a situation it doesn't know how to handle.
    HTTP_STATUS_NOT_IMPLEMENTED = 501  # The request method is not supported by the server and cannot be handled.
