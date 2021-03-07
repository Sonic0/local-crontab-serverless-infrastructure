from typing import Any, NoReturn

from http_status_constants import HttpStatusCode


class ApiError(Exception):
    """ Exception class for managed errors """

    def __init__(self, error: Any, msg=None, http_status_code=HttpStatusCode.HTTP_STATUS_BAD_REQUEST) -> NoReturn:
        if msg is None:  # default useful error message
            msg = f"An error occurred with API -> {error}"
        super().__init__(error)
        self.msg = msg
        self.http_status_code = http_status_code
        self.error = error

    def __str__(self) -> str:
        return str(self.error)
