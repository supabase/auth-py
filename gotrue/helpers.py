from time import time
from typing import Any, Callable, TypeVar, Union
from urllib.parse import quote

from httpx import HTTPError, Response

from .types import APIError, Session, User

T = TypeVar("T")


def encode_uri_component(uri: str) -> str:
    return quote(uri.encode("utf-8"))


def parse_response(response: Response, func: Callable[[Any], T]) -> T:
    try:
        response.raise_for_status()
        json = response.json()
        result = func(json)
        if isinstance(result, Session) and result.expires_in and not result.expires_at:
            result.expires_at = round(time()) + result.expires_in
        return result
    except HTTPError:
        json = response.json()
        raise APIError.from_dict(json)


def parse_session_or_user(arg: Any) -> Union[Session, User]:
    if "access_token" in arg:
        return Session(**arg)
    return User(**arg)
