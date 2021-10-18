from typing import Any, Callable, TypeVar, Union
from urllib.parse import quote

from httpx import HTTPError, Response

from .types import ApiError, Session, User

T = TypeVar("T")


def encode_uri_component(uri: str) -> str:
    return quote(uri.encode("utf-8"))


def parse_response(response: Response, func: Callable[[Any], T]) -> T:
    try:
        response.raise_for_status()
        json = response.json()
        return func(json)
    except HTTPError:
        raise ApiError(message=response.text, status=response.status_code)


def parse_session_or_user(arg: Any) -> Union[Session, User]:
    if "access_token" in arg:
        Session.from_dict(arg)
    return User.from_dict(arg)
