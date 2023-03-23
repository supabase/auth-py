from __future__ import annotations

from base64 import b64decode
from json import loads
from typing import Any, Union, cast

from httpx import HTTPStatusError

from .errors import AuthApiError, AuthError, AuthRetryableError, AuthUnknownError
from .types import (
    AuthResponse,
    GenerateLinkProperties,
    GenerateLinkResponse,
    Session,
    User,
    UserResponse,
)


def parse_auth_response(data: Any) -> AuthResponse:
    session: Union[Session, None] = None
    if (
        "access_token" in data
        and "refresh_token" in data
        and "expires_in" in data
        and data["access_token"]
        and data["refresh_token"]
        and data["expires_in"]
    ):
        session = Session.parse_obj(data)
    user = User.parse_obj(data["user"]) if "user" in data else User.parse_obj(data)
    return AuthResponse(session=session, user=user)


def parse_link_response(data: Any) -> GenerateLinkResponse:
    properties = GenerateLinkProperties(
        action_link=data.get("action_link"),
        email_otp=data.get("email_otp"),
        hashed_token=data.get("hashed_token"),
        redirect_to=data.get("redirect_to"),
        verification_type=data.get("verification_type"),
    )
    user = User.parse_obj({k: v for k, v in data.items() if k not in properties.dict()})
    return GenerateLinkResponse(properties=properties, user=user)


def parse_user_response(data: Any) -> UserResponse:
    if "user" not in data:
        data = {"user": data}
    return UserResponse.parse_obj(data)


def get_error_message(error: Any) -> str:
    props = ["msg", "message", "error_description", "error"]
    filter = (
        lambda prop: prop in error if isinstance(error, dict) else hasattr(error, prop)
    )
    return next((error[prop] for prop in props if filter(prop)), str(error))


def looks_like_http_status_error(exception: Exception) -> bool:
    return isinstance(exception, HTTPStatusError)


def handle_exception(exception: Exception) -> AuthError:
    if not looks_like_http_status_error(exception):
        return AuthRetryableError(get_error_message(exception), 0)
    error = cast(HTTPStatusError, exception)
    try:
        network_error_codes = [502, 503, 504]
        if error.response.status_code in network_error_codes:
            return AuthRetryableError(
                get_error_message(error), error.response.status_code
            )
        json = error.response.json()
        return AuthApiError(get_error_message(json), error.response.status_code or 500)
    except Exception as e:
        return AuthUnknownError(get_error_message(error), e)


def decode_jwt_payload(token: str) -> Any:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT is not valid: not a JWT structure")
    base64Url = parts[1]
    # Addding padding otherwise the following error happens:
    # binascii.Error: Incorrect padding
    base64UrlWithPadding = base64Url + "=" * (-len(base64Url) % 4)
    return loads(b64decode(base64UrlWithPadding).decode("utf-8"))
