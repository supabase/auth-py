from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from gotrue.utils import _parse_none


@dataclass
class ApiError(BaseException):
    message: str
    status: int

    def __post_init__(self) -> None:
        self.message = str(self.message)
        self.status = int(str(self.status))

    @staticmethod
    def from_dict(data: dict) -> "ApiError":
        return ApiError(**data)


@dataclass
class User:
    action_link: Optional[str]
    app_metadata: Dict[str, Any]
    aud: str
    confirmation_sent_at: Optional[str]
    confirmed_at: Optional[str]
    created_at: str
    email: Optional[str]
    email_confirmed_at: Optional[str]
    id: str
    last_sign_in_at: Optional[str]
    phone: Optional[str]
    phone_confirmed_at: Optional[str]
    recovery_sent_at: Optional[str]
    role: Optional[str]
    updated_at: Optional[str]
    user_metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        self.action_link = _parse_none(self.action_link, str)
        self.app_metadata = dict(self.app_metadata)
        self.aud = str(self.aud)
        self.confirmation_sent_at = _parse_none(self.confirmation_sent_at, str)
        self.confirmed_at = _parse_none(self.confirmed_at, str)
        self.created_at = str(self.created_at)
        self.email = _parse_none(self.email, str)
        self.email_confirmed_at = _parse_none(self.email_confirmed_at, str)
        self.id = str(self.id)
        self.last_sign_in_at = _parse_none(self.last_sign_in_at, str)
        self.phone = _parse_none(self.phone, str)
        self.phone_confirmed_at = _parse_none(self.phone_confirmed_at, str)
        self.recovery_sent_at = _parse_none(self.recovery_sent_at, str)
        self.role = _parse_none(self.role, str)
        self.updated_at = _parse_none(self.updated_at, str)
        self.user_metadata = dict(self.user_metadata)

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(**data)


@dataclass
class Session:
    access_token: str
    expires_at: Optional[int]
    """A timestamp of when the token will expire. Returned when a login is confirmed."""
    expires_in: Optional[int]
    """The number of seconds until the token expires (since it was issued).
    Returned when a login is confirmed."""
    provider_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str
    user: Optional[User]

    def __post_init__(self) -> None:
        self.access_token = str(self.access_token)
        self.expires_at = _parse_none(self.expires_at, lambda x: int(str(x)))
        self.expires_in = _parse_none(self.expires_in, lambda x: int(str(x)))
        self.provider_token = _parse_none(self.provider_token, str)
        self.refresh_token = _parse_none(self.refresh_token, str)
        self.token_type = str(self.token_type)
        if self.user:
            self.user.__post_init__()

    @staticmethod
    def from_dict(data: dict) -> "Session":
        user: Optional[User] = None
        user_data = data.get("user")
        if user_data:
            user = User.from_dict(user_data)
        del data["user"]
        return Session(**data, user=user)


class LinkType(str, Enum):
    """The type of link."""

    signup = "signup"
    magiclink = "magiclink"
    recovery = "recovery"
    invite = "invite"
