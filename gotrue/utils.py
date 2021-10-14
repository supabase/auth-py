from typing import Any, Callable, Optional, TypeVar, Union

from requests import Response

from gotrue.models import ApiError, Session, User

T = TypeVar("T")


def _parse_none(
    value: Optional[T],
    func: Callable[[Any], T],
) -> Optional[T]:
    if value is None:
        return None
    return func(value)


def _parse_response(response: Response, func: Callable[[Any], T]) -> T:
    if response.status_code == 200:
        json = response.json()
        data = json.get("data")
        error = json.get("error")
        if error:
            raise ApiError.from_dict(error)
        if data:
            return func(data)
        raise ApiError(message="data and error are null at the same time", status=-1)
    else:
        raise ApiError(message=response.text, status=response.status_code)


def _parse_session_or_user(arg: Any) -> Union[Session, User]:
    if "access_token" in arg:
        Session.from_dict(arg)
    return User.from_dict(arg)
