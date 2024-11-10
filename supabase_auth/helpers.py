from __future__ import annotations

import base64
import hashlib
import re
import secrets
import string
from base64 import urlsafe_b64decode
from datetime import datetime
from json import loads
from typing import Any, Dict, Optional, Type, TypeVar, cast
from urllib.parse import urlparse

from httpx import HTTPStatusError, Response
from pydantic import BaseModel

from .constants import API_VERSION_HEADER_NAME, API_VERSIONS
from .errors import (
    AuthApiError,
    AuthError,
    AuthRetryableError,
    AuthUnknownError,
    AuthWeakPasswordError,
)
from .types import (
    AuthOtpResponse,
    AuthResponse,
    GenerateLinkProperties,
    GenerateLinkResponse,
    LinkIdentityResponse,
    Session,
    SSOResponse,
    User,
    UserResponse,
)

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)
BASE64URL_REGEX = r"^([a-z0-9_-]{4})*($|[a-z0-9_-]{3}$|[a-z0-9_-]{2}$)$"


def model_validate(model: Type[TBaseModel], contents) -> TBaseModel:
    """Compatibility layer between pydantic 1 and 2 for parsing an instance
    of a BaseModel from varied"""
    try:
        # pydantic > 2
        return model.model_validate(contents)
    except AttributeError:
        # pydantic < 2
        return model.parse_obj(contents)


def model_dump(model: BaseModel) -> Dict[str, Any]:
    """Compatibility layer between pydantic 1 and 2 for dumping a model's contents as a dict"""
    try:
        # pydantic > 2
        return model.model_dump()
    except AttributeError:
        # pydantic < 2
        return model.dict()


def model_dump_json(model: BaseModel) -> str:
    """Compatibility layer between pydantic 1 and 2 for dumping a model's contents as json"""
    try:
        # pydantic > 2
        return model.model_dump_json()
    except AttributeError:
        # pydantic < 2
        return model.json()


def parse_auth_response(data: Any) -> AuthResponse:
    session: Optional[Session] = None
    if (
        "access_token" in data
        and "refresh_token" in data
        and "expires_in" in data
        and data["access_token"]
        and data["refresh_token"]
        and data["expires_in"]
    ):
        session = model_validate(Session, data)
    user_data = data.get("user", data)
    user = model_validate(User, user_data) if user_data else None
    return AuthResponse(session=session, user=user)


def parse_auth_otp_response(data: Any) -> AuthOtpResponse:
    return model_validate(AuthOtpResponse, data)


def parse_link_identity_response(data: Any) -> LinkIdentityResponse:
    return model_validate(LinkIdentityResponse, data)


def parse_link_response(data: Any) -> GenerateLinkResponse:
    properties = GenerateLinkProperties(
        action_link=data.get("action_link"),
        email_otp=data.get("email_otp"),
        hashed_token=data.get("hashed_token"),
        redirect_to=data.get("redirect_to"),
        verification_type=data.get("verification_type"),
    )
    user = model_validate(
        User, {k: v for k, v in data.items() if k not in model_dump(properties)}
    )
    return GenerateLinkResponse(properties=properties, user=user)


def parse_user_response(data: Any) -> UserResponse:
    if "user" not in data:
        data = {"user": data}
    return model_validate(UserResponse, data)


def parse_sso_response(data: Any) -> SSOResponse:
    return model_validate(SSOResponse, data)


def get_error_message(error: Any) -> str:
    props = ["msg", "message", "error_description", "error"]
    filter = lambda prop: (
        prop in error if isinstance(error, dict) else hasattr(error, prop)
    )
    return next((error[prop] for prop in props if filter(prop)), str(error))


def get_error_code(error: Any) -> str:
    return error.get("error_code", None) if isinstance(error, dict) else None


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
        data = error.response.json()

        error_code = None
        response_api_version = parse_response_api_version(error.response)

        if (
            response_api_version
            and datetime.timestamp(response_api_version)
            >= API_VERSIONS.get("2024-01-01").get("timestamp")
            and isinstance(data, dict)
            and data
            and isinstance(data.get("code"), str)
        ):
            error_code = data.get("code")
        elif (
            isinstance(data, dict) and data and isinstance(data.get("error_code"), str)
        ):
            error_code = data.get("error_code")

        if error_code is None:
            if (
                isinstance(data, dict)
                and data
                and isinstance(data.get("weak_password"), dict)
                and data.get("weak_password")
                and isinstance(data.get("weak_password"), list)
                and len(data.get("weak_password"))
            ):
                return AuthWeakPasswordError(
                    get_error_message(data),
                    error.response.status_code,
                    data.get("weak_password").get("reasons"),
                )
        elif error_code == "weak_password":
            return AuthWeakPasswordError(
                get_error_message(data),
                error.response.status_code,
                data.get("weak_password", {}).get("reasons", {}),
            )

        return AuthApiError(
            get_error_message(data),
            error.response.status_code or 500,
            error_code,
        )
    except Exception as e:
        return AuthUnknownError(get_error_message(error), e)


def decode_jwt_payload(token: str) -> Any:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT is not valid: not a JWT structure")
    base64url = parts[1]
    # Addding padding otherwise the following error happens:
    # binascii.Error: Incorrect padding
    base64url_with_padding = base64url + "=" * (-len(base64url) % 4)
    return loads(urlsafe_b64decode(base64url_with_padding).decode("utf-8"))


def generate_pkce_verifier(length=64):
    """Generate a random PKCE verifier of the specified length."""
    if length < 43 or length > 128:
        raise ValueError("PKCE verifier length must be between 43 and 128 characters")

    # Define characters that can be used in the PKCE verifier
    charset = string.ascii_letters + string.digits + "-._~"

    return "".join(secrets.choice(charset) for _ in range(length))


def generate_pkce_challenge(code_verifier):
    """Generate a code challenge from a PKCE verifier."""
    # Hash the verifier using SHA-256
    verifier_bytes = code_verifier.encode("utf-8")
    sha256_hash = hashlib.sha256(verifier_bytes).digest()

    return base64.urlsafe_b64encode(sha256_hash).rstrip(b"=").decode("utf-8")


API_VERSION_REGEX = r"^2[0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])$"


def parse_response_api_version(response: Response):
    api_version = response.headers.get(API_VERSION_HEADER_NAME)

    if not api_version:
        return None

    if re.search(API_VERSION_REGEX, api_version) is None:
        return None

    try:
        dt = datetime.strptime(api_version, "%Y-%m-%d")
        return dt
    except Exception as e:
        return None


def is_http_url(url: str) -> bool:
    return urlparse(url).scheme in {"https", "http"}


def is_valid_jwt(value: str) -> bool:
    """Checks if value looks like a JWT, does not do any extra parsing."""
    if not isinstance(value, str):
        return False

    # Remove trailing whitespaces if any.
    value = value.strip()

    # Remove "Bearer " prefix if any.
    if value.startswith("Bearer "):
        value = value[7:]

    # Valid JWT must have 2 dots (Header.Paylod.Signature)
    if value.count(".") != 2:
        return False

    for part in value.split("."):
        if not re.search(BASE64URL_REGEX, part, re.IGNORECASE):
            return False

    return True
