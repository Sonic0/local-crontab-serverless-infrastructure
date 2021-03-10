import logging
import json
from typing import Optional, Dict, Union, NamedTuple, Tuple, TypedDict, Any
from lambda_decorators import dump_json_body, load_json_body
from local_crontab import Converter
from local_crontab.converter import WrongTimezoneError
# Utilities to handle input/output from/to API Gateway
from api_gateway_parser.api_gateway_request import APIGatewayRequest
from api_gateway_parser.api_gateway_response import APIGatewayResponse
from api_gateway_parser.http_status_constants import HttpStatusCode

log = logging.getLogger(__name__)
log_level = logging.DEBUG
logging.getLogger().setLevel(log_level)


class UnsupportedMethodException(Exception):
    pass


def is_correct_http_method(request: APIGatewayRequest) -> bool:
    """
    Request filter that enforces the request method is `POST`.

    :param request: Parsed HTTP request from API Gateway
    :return: Is HTTP method correct
    :raises UnsupportedMethodException: the request method is not POST
    """
    correct = False
    method = request.http
    if method != "POST":
        raise UnsupportedMethodException(f'unsupported method "{method}"')
    else:
        return correct


@load_json_body()  # auto-deserialize http body from JSON
@dump_json_body()  # auto-serialization http body to JSON
def lambda_handler(event, context: Dict) -> Union[Dict[Any, Any]]:
    """


    Parameters
    ----------
    event: dict, required


    context: object, required


    Returns
    ------

    """
    log.debug(f"Received event from API G.: {json.dumps(event, indent=2)}")
    api_request = APIGatewayRequest(event, context)
    log.debug(f"Api G. request: {api_request}")

    try:
        is_correct_http_method(api_request)
        response_body = Converter(api_request.body.get('cron'), api_request.body.get('timezone')).to_utc_crons()
    except UnsupportedMethodException as ex:
        log.critical(f"Internal Error: {ex}")
        api_response = APIGatewayResponse(
            status_code=HttpStatusCode.HTTP_STATUS_BAD_REQUEST,
            body={'message': str(ex)})
    except WrongTimezoneError as ex:
        log.critical(f"Internal Error: {ex}")
        api_response = APIGatewayResponse(
            status_code=HttpStatusCode.HTTP_STATUS_BAD_REQUEST,
            body={'message': str(ex)})
    except Exception as ex:
        log.critical(f"Internal Error: {ex}")
        api_response = APIGatewayResponse(
            status_code=HttpStatusCode.HTTP_STATUS_INTERNAL_SERVER_ERROR,
            body={'message': str(ex)})
    else:
        api_response = APIGatewayResponse(body=response_body)
    finally:
        log.debug(f"Api Gateway res: {json.dumps(api_response.serialized, default=str, indent=2)}")

    return api_response.serialized
